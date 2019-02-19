import re

from dceu2019.apps.invoices import billy, models, ticketbutler
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from djmoney.money import Money

re_vatid_country = re.compile(r"^([a-zA-Z]+).*$")


class Command(BaseCommand):
    help = 'Fetches all unique ticket types and prices in a JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only-known-invoices',
            action='store_true',
            dest='only_known',
            help='Great for testing and not creating invoices or payments in Billy',
        )
        parser.add_argument(
            '--skip-synced',
            action='store_true',
            dest='skip_synced',
            help='Skip things that are already synced',
        )

    def handle(self, *args, **options):

        self.only_known = options['only_known']
        self.skip_synced = options['skip_synced']

        self.client = billy.BillyClient(settings.BILLY_TOKEN)
        self.organization_id = billy.get_organization_id(self.client)

        tb_data = ticketbutler.TicketbutlerClient().request()

        self.valid_countries = billy.get_countries(self.client)

        if 'orders' not in tb_data.keys():
            raise CommandError("Not valid JSON data. Were you logged in when you fetched the file?")

        for order in tb_data['orders']:

            self.create_invoice(order)

    def create_invoice(self, order):  # noqa:max-complexity=18
        """
        Creates an invoice from a dictionary of ticketbutler API output
        """

        assert len(order['order_lines']) == 1

        order_id = order['order_id']

        if not order['state'] == 'PAID':
            self.stdout.write(self.style.WARNING("Skipping unpaid order: {}".format(order['order_id'])))
            return

        if any(t['ticket_refund'] for t in order['tickets']):
            self.stdout.write(self.style.WARNING("Skipping refunded order: {}".format(order['order_id'])))
            return

        if order['order_lines'][0]['discount_total'] is not None:
            self.stdout.write(self.style.WARNING("Skipping manually invoiced/discounted ticket: {}".format(order_id)))
            return

        if self.only_known and order_id not in billy.TICKETBUTLER_IGNORE_LIST:
            self.stdout.write(self.style.WARNING("Only processing known invoices, skipping {}".format(order_id)))
            return

        # Object containing all created tickets, to have an invoice relation
        # appended later
        ticketbutler_tickets = []

        order_info = order['order_lines'][0]
        currency = order['currency']
        when = order['date']
        first_name = order['address']['first_name'] or ""
        last_name = order['address']['last_name'] or ""
        person_name = " ".join([first_name, last_name])
        email = order['address']['email']
        phone = order['address']['phone']
        vat_id = order['address']['vat_number']
        company = order['address']['business_name']
        vat_rate = 0.25
        # Price in Ticketbutler includes VAT, so remove it
        price = float(order_info['price']) * 1.0 / (1.0 + vat_rate)
        amount = order_info['quantity']
        billy_product_id = billy.TICKETBUTLER_PRODUCT_ID_MAPPING[order_info['title']]

        # We need to ask manually
        country = None
        address = order['address']['address']

        for ticket in order['tickets']:

            # sprints = filter(
            #     lambda q: q['uuid']=="baff5d43c67f4ff7aedf2968e06e1825",
            #     ticket['questions']
            # )[0]

            ticketbutler_tickets.append(models.TicketbutlerTicket.get_or_create(
                ticket['email'],
                ticket['full_name'],
                order_id,
                None  # Sprints are not detected yet
            ))

        # Process manually created invoices by preferring data from the
        # accounting system
        if order_id in billy.TICKETBUTLER_IGNORE_LIST:

            self.stdout.write(self.style.WARNING("Manually processed, fetching PDF and creating data from Billy {}".format(order_id)))
            billy_invoice_id = billy.TICKETBUTLER_IGNORE_LIST[order_id]
            billy_invoice = billy.get_invoice(self.client, billy_invoice_id)
            billy_contact = billy.get_contact(self.client, billy_invoice['contactId'])
            billy.save_invoice_pdf(self.client, billy_invoice_id)

            try:
                contact = models.BillyInvoiceContact.objects.get(billy_id=billy_invoice['contactId'])
            except models.BillyInvoiceContact.DoesNotExist:
                contact = models.BillyInvoiceContact(billy_id=billy_invoice['contactId'])

            contact.name = billy_contact['name']
            contact.type = billy_contact['type']
            contact.person_name = billy_contact['contactPersons'][0]['name'] if 'contactPersons' in billy_contact else None
            contact.person_email = billy_contact['contactPersons'][0]['email'] if 'contactPersons' in billy_contact else None
            contact.country_code = billy_contact['countryId']
            contact.street = billy_contact['street']
            contact.city_text = billy_contact['cityText']
            contact.zipcode_text = billy_contact['zipcodeText']
            contact.phone = billy_contact['phone']
            contact.registration_no = billy_contact['registrationNo']
            contact.ticketbutler_orderid = order_id

            contact.save()

            try:
                invoice = models.Invoice.objects.get(billy_id=billy_invoice_id)
            except models.Invoice.DoesNotExist:
                invoice = models.Invoice(billy_id=billy_invoice_id)

            invoice.billy_contact = contact
            invoice.billy_product_id = billy_product_id
            invoice.ticketbutler_orderid = order_id
            invoice.when = when
            invoice.price = Money(price, currency)
            invoice.vat = vat_rate
            invoice.amount = amount
            invoice.ticket_type_name = order_info['title']

            invoice.save()

            return

        # Try to figure out country

        confirmed = False

        if self.skip_synced and models.Invoice.objects.filter(ticketbutler_orderid=order_id).exists():
            self.stdout.write(self.style.SUCCESS("Already sync'ed, skipping {}".format(order_id)))
            return

        while not confirmed:

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
                country = country.strip().upper()
                if country == "":
                    country = default_country
                if country not in self.valid_countries:
                    country = None

            street = None
            while street is None:
                street = input("Street? ".format(address))

            zip_code = None
            while zip_code is None:
                zip_code = input("Zip? ".format(address))

            city = None
            while city is None:
                city = input("City? ".format(address))

            confirmed = input("Confirm this [Y/n]").lower() in ["y", ""]

        try:
            contact = models.BillyInvoiceContact.objects.get(ticketbutler_orderid=order_id)
            self.stdout.write(self.style.WARNING("Contact already existed: {}".format(order_id)))
        except models.BillyInvoiceContact.DoesNotExist:
            contact = models.BillyInvoiceContact.objects.create(
                name=company or person_name,
                type="company" if company else "person",
                person_name=person_name,
                person_email=email,
                country_code=country.strip().upper(),
                street=street,
                city_text=city,
                zipcode_text=zip_code,
                phone=phone,
                registration_no=vat_id,
                ticketbutler_orderid=order_id,
            )
            self.contact2billy(contact)
            self.stdout.write(self.style.SUCCESS("Created a contact in Billy"))

        try:
            invoice = models.Invoice.objects.get(ticketbutler_orderid=order_id)
            self.stdout.write(self.style.WARNING("Invoice already existed: {}".format(order_id)))

        except models.Invoice.DoesNotExist:

            invoice = models.Invoice.objects.create(
                billy_contact=contact,
                billy_product_id=billy_product_id,
                ticketbutler_orderid=order_id,
                when=when,
                price=Money(price, currency),
                vat=vat_rate,
                amount=amount,
                ticket_type_name=order_info['title'],
            )

            if order_id in billy.TICKETBUTLER_IGNORE_LIST:
                billy_invoice = billy.get_invoice(
                    self.client,
                    billy.TICKETBUTLER_IGNORE_LIST[order_id]
                )
                invoice.billy_id = billy_invoice['id']
                invoice.synced = True
                invoice.save()
                self.stdout.write(self.style.SUCCESS("Invoice found in ignore list: {}".format(order_id)))
            else:
                self.invoice2billy(invoice)
                self.stdout.write(self.style.SUCCESS("Invoice created in Billy"))
                self.create_payment(invoice, contact)

        # Download invoice PDF
        billy.save_invoice_pdf(self.client, invoice.billy_id)
        self.stdout.write(self.style.SUCCESS("PDF downloaded and saved."))

        for ticket in ticketbutler_tickets:
            ticket.invoice = invoice
            ticket.save()

    def create_payment(self, invoice, contact):

        if input("Create payment [y/N]").lower() == "y":
            billy.create_payment(
                self.client,
                self.organization_id,
                invoice.billy_id,
                contact.billy_id,
                settings.BILLY_TICKET_ACCOUNT,
                float(float(invoice.price.amount) * float(1 + invoice.vat)) * invoice.amount,
                invoice.price.currency,
                invoice.when
            )
            self.stdout.write(self.style.SUCCESS("Payment created in Billy"))

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
