import requests

from django.conf import settings


#: Mapping of our ticket types in Ticketbutler to product ids in Billy
TICKETBUTLER_PRODUCT_ID_MAPPING = {
    'Business': 'yp9oH3ZWSH6aJFKBYOdKQQ',
    'Business EARLY BIRD': 'eWF0le75ScaB6cxgSG0mYQ',
    'Business Supporter': 'L1SSAgzpTUuIsL79BXMTeg',
    'Business Supporter EARLY BIRD': 'Od7vH04ZQE6GXxS3lE1SCg',
    'Individual': 'mu89bJt9QU670vEYJkXhcw',
    'Individual EARLY BIRD': '9Sk7hbw0Sci3QLTbMmNnoA',
    'Individual Supporter EARLY BIRD': '0vWktrh2SCnthhVrk9vVEg', 
    'Individual Supporter': 'IZo5OGZFQxmF2qUT5ErZlw',
    'Student/Concession': 'vXSLt7lhTvKJGqz4iaR6Wg',
    'Student/Concession EARLY BIRD': 'KufXneavQdaune3J6hxSxg',
    'Test ticket': None,
}


# Reusable class for sending requests to the Billy API
class BillyClient:
    def __init__(self, apiToken):
        self.apiToken = apiToken

    def request(self, method, url, body):
        baseUrl = 'https://api.billysbilling.com/v2'

        try:
            response = {
                'GET': requests.get(
                    baseUrl + url,
                    headers={'X-Access-Token': self.apiToken}
                ),
                'POST': requests.post(
                    baseUrl + url,
                    json=body,
                    headers={'X-Access-Token': self.apiToken}
                ),
            }[method]
            status_code = response.status_code
            raw_body = response.text

            if status_code >= 400:
                raise requests.exceptions.RequestException(
                    '{}: {} failed with {:d} - {}'
                    .format(method, url, status_code, raw_body)
                )

            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            raise e


# Creates a contact. The server replies with a list of contacts and we
# return the id of the first contact of the list
def createContact(client, organizationId):
    contact = {
        'organizationId': organizationId,
        'name': 'John',
        'countryId': 'DK'
    }
    response = client.request('POST', '/contacts', {'contact': contact})

    return response['contacts'][0]['id']


# Creates a product. The server replies with a list of products and we
# return the id of the first product of the list
def createProduct(client, organizationId):
    product = {
        'organizationId': organizationId,
        'name': 'Pens',
        'prices': [{
            'unitPrice': 200,
            'currencyId': 'DKK'
        }]
    }
    response = client.request('POST', '/products', {'product': product})

    return response['products'][0]['id']


# Creates an invoice, the server replies with a list of invoices and we
# return the id of the first invoice of the list
def createInvoice(client, organizationId, contactId, productId):
    invoice = {
        'organizationId': organizationId,
        'invoiceNo': 65432,
        'entryDate': '2013-11-14',
        'contactId': contactId,
        'lines': [{
            'productId': productId,
            'unitPrice': 200
        }]
    }
    response = client.request('POST', '/invoices', {'invoice': invoice})

    return response['invoices'][0]['id']


# Get id of organization associated with the API token.
def getOrganizationId(client):
    response = client.request('GET', '/organization', None)

    return response['organization']['id']


# Gets a invoice by its Id
def get_invoice(client, invoiceId):
    response = client.request('GET', '/invoices', invoiceId)

    return response['invoices'][0]



def print_products(client):
    response = client.request('GET', '/products', None)

    for product in response['products']:
        print(product['name'] + ", " + product['id'])


def main():
    client = BillyClient(settings.BILLY_TOKEN)

    currentOrganizationId = getOrganizationId(client)
    # newContactId = createContact(client, currentOrganizationId)
    # newProductId = createProduct(client, currentOrganizationId)
    # newinvoiceId = createInvoice(client, currentOrganizationId, newContactId, newProductId)
    # newlyCreatedInvoice = get_invoice(client, newinvoiceId)

    print_products(client)


if __name__ == '__main__':
    main()
