import json
import os

from django.core.management.base import BaseCommand, CommandError

from dceu2019.apps.invoices import billy


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
        
        ticket_types = set()
        
        for ticket_orders in tb_data['orders']:
            for order in ticket_orders['order_lines']:
                ticket_types.add(order['title'])
        
        self.stdout.write(self.style.SUCCESS("Sold {} ticket types".format(len(ticket_types))))

        all_okay = True
        for type_name in ticket_types:
            if not type_name in billy.TICKETBUTLER_PRODUCT_ID_MAPPING.keys():
                self.stdout.write(self.style.ERROR("Ticket type not found: {}".format(type_name)))
                all_okay = False
                
        if all_okay:
            self.stdout.write(self.style.SUCCESS("All good, no new mappings need to be created"))
