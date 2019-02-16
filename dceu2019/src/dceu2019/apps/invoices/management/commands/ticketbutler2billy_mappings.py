import json
import os
import re

from django.core.management.base import BaseCommand, CommandError

from dceu2019.apps.invoices import billy


re_vatid_country = re.compile(r"^([a-zA-Z]+).*$")


class Command(BaseCommand):
    help = 'Fetches all unique ticket types and prices in a JSON'


    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **options):
        
        json_file = options['json_file']
        
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
        
        if not order['state'] == 'PAID':
            self.stdout.write(self.style.ERROR("Skipping unpaid order: {}".format(order['order_id'])))
            return
        
        order_id = order['order_id']

        currency = order['currency']
        
        when = order['date']
        
        first_name = order['address']['first_name']
        last_name = order['address']['last_name']
        email = order['address']['email']
        phone = order['address']['phone']
        vat_id = order['address']['vat_number']
        company = order['address']['business_name']

        address = order['address']['address']
        
        country = None
        
        # Try to figure out country
        
        print("Order ID: {}".format(order_id))
        print("Address is: {}".format(address))
        default_country = "DK"
        
        if vat_id:
            country_match = re_vatid_country.match(vat_id)
            if country_match:
                default_country = country_match.group(1)

        while country is None:
            country = input("What country code to use? [{}] ".format(default_country))
            if 2 < len(country) < 4:
                country = None
        
