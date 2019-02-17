import json
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from djmoney.money import Money

from dceu2019.apps.invoices import billy
from dceu2019.apps.invoices import models

re_vatid_country = re.compile(r"^([a-zA-Z]+).*$")


class Command(BaseCommand):
    help = 'Fetches all unique ticket types and prices in a JSON'


    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **options):
        
        json_file = options['json_file']
        
        self.client = billy.BillyClient(settings.BILLY_TOKEN)
        self.organization_id = billy.get_organization_id(self.client)
        
        if not os.path.isfile(json_file):
            raise CommandError("Not found: {}".format(json_file))
        
        tb_data = json.load(open(json_file, 'r'))

        if not 'orders' in tb_data.keys():
            raise CommandError("Not valid JSON data. Were you logged in when you fetched the file?")

        for order in tb_data['orders']:
            
            self.create_invoice(order)
                

    def create_invoice(self, order):
        """
        Creates an invoice from a dictionary of ticketbutler API output
        """
        
        assert len(order['order_lines']) == 1        
        
        assert order['order_lines'][0]['discount_total'] is None
        
        if not order['state'] == 'PAID':
            self.stdout.write(self.style.ERROR("Skipping unpaid order: {}".format(order['order_id'])))
            return
        
        order_id = order['order_id']

        currency = order['currency']
        
        when = order['date']
        
        first_name = order['address']['first_name'] or ""
        last_name = order['address']['last_name'] or ""
        person_name = " ".join([first_name, last_name])
        email = order['address']['email']
        phone = order['address']['phone']
        vat_id = order['address']['vat_number']
        company = order['address']['business_name']

        address = order['address']['address']
        
        country = None
        
        # Try to figure out country
        
        print("Order ID: {}".format(order_id))
        print("Person: {}".format(person_name))
        print("Company: {}".format(company))
        print("VAT ID: {}".format(vat_id))
        print("Email: {}".format(email))
        print("Address: {}".format(address))
        default_country = "DK"
        
        if vat_id:
            country_match = re_vatid_country.match(vat_id)
            if country_match:
                default_country = country_match.group(1)

        while country is None:
            country = input("What country code to use? [{}] ".format(default_country))
            if country == "":
                country = default_country
            if 2 < len(country) < 4:
                country = None
        
        street = None
        while street is None:
            street = input("Street? [{}] ".format(address))

        zip_code = None
        while zip_code is None:
            zip_code = input("Zip? [{}] ".format(address))

        city = None
        while city is None:
            city = input("City? [{}] ".format(address))

        order_info = order['order_lines'][0]
        
        billy_product_id = billy.TICKETBUTLER_PRODUCT_ID_MAPPING[order_info['title']]
        price = order_info['price']
        amount = order_info['quantity']
        
        contact = models.BillyInvoiceContact.objects.create(
            name=company or person_name,
            type="company" if company else "person",
            person_name=person_name,
            person_email=email,
            country_code=country.upper(),
            street=street,
            city_text=city,
            zipcode_text=zip_code,
            phone=phone,
            registration_no=vat_id,
        )
        
        self.contact2billy(contact)
        
        self.stdout.write(self.style.SUCCESS("Created a contact in Billy"))
        
        invoice = models.Invoice.objects.create(
            billy_contact=contact,
            billy_product_id=billy_product_id,
            ticketbutler_orderid=order_id,
            when=when,
            price=Money(price, currency),
            vat=0.25,
            amount=amount,
            ticket_type_name=order_info['title'],
            
        )
        
        self.invoice2billy(invoice)
        
        self.stdout.write(self.style.SUCCESS("Invoice created in Billy"))
        
        
    def contact2billy(self, contact):
        
        contact_id = billy.create_contact(
            self.client,
            self.organization_id,
            contact.type,
            contact.name,
            contact.country_code,
            contact.street,
            contact.city_text,
            contact.zipcode_text,
            contact.phone,
            contact.registration_no,
        )
        contact.billy_id = contact_id
        contact.synced = True
        contact.save()
        person_id = billy.create_contact_person(
            self.client,
            self.organization_id,
            contact_id,
            contact.person_name,
            contact.country_code,
            contact.person_email
        )        
        contact.billy_person_id = person_id
        contact.save()
    
    def invoice2billy(self, invoice):
        
        billy_id = billy.create_invoice(
            self.client,
            self.organization_id,
            invoice.billy_contact.billy_id,
            invoice.billy_product_id, 
            float(invoice.price.amount),
            invoice.amount,
            str(invoice.price.currency),
            invoice.when,
        )
        invoice.synced = True
        invoice.billy_id = billy_id
        invoice.save()