import requests

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

TICKETBUTLER_IGNORE_LIST = {
    "duL103749": "cZcUunyMSQeleC1MkSjRDQ",
    "duL104800": "kxVxDrhyR4qhEt1oOjcIeQ",
    # "duL105236", Never found an invoice manually created for this.
    "duL105270": "OX394htpTQ6lofqbZLe2dA",
    "duL105671": "86XosNdcRaeLshWFIOEo0g",
    "duL105274": "AnsSABPbRDWjPEI0skUwWA",
    "duL105037": "ikvKb9rIRvSbgSQrxnDaFg",
    "duL103267": "3x8H7ReTR0KFDMODonVuQg",
    "duL105594": "QphSa5EPTyiXI3rzSyMJVg",
    "duL104454": "wNBtx7yDS5uyASIFfnyekw",
}


# Reusable class for sending requests to the Billy API
class BillyClient:

    def __init__(self, apiToken):
        self.apiToken = apiToken

    def request(self, method, url, body):
        baseUrl = 'https://api.billysbilling.com/v2'

        try:

            # Yay, the API docs don't work, so we need to APPEND the third arg
            # to the URL...
            if method == 'GET':
                if body:
                    abs_url = "/".join((baseUrl + url, body))
                else:
                    abs_url = baseUrl + url
                response = getattr(requests, method.lower())(
                    abs_url,
                    headers={
                        'X-Access-Token': self.apiToken,
                    },
                )
            else:
                response = getattr(requests, method.lower())(
                    baseUrl + url,
                    headers={
                        'X-Access-Token': self.apiToken,
                        'Content-Type': "application/json",
                    },
                    json=body,
                )
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


def create_contact_person(client, organization_id, contact_id, name, country_code, email=None):
    """
    Creates a contact person object in Billy:
    https://www.billy.dk/api/#v2contactpersons
    """
    contact = {
        'name': name,
        'email': email,
        'isPrimary': True,
        'contactId': contact_id,
    }
    response = client.request('POST', '/contactPersons', {'contactPerson': contact})

    return response['contactPersons'][0]['id']


def create_contact(client,
                   organization_id,
                   contact_type,
                   name,
                   country_code,
                   street,
                   city,
                   zip_code,
                   phone,
                   vat_id):
    """
    https://www.billy.dk/api/#v2contacts
    """
    contact = {
        'organizationId': organization_id,
        'type': contact_type,
        'name': name,
        'countryId': country_code.strip().upper(),
        'street': street,
        'cityText': city,
        'zipcodeText': zip_code,
        'phone': phone,
        'registrationNo': vat_id,
        'isCustomer': True,
        'paymentTermsDays': 15,
    }
    response = client.request('POST', '/contacts', {'contact': contact})

    return response['contacts'][0]['id']


# Creates an invoice, the server replies with a list of invoices and we
# return the id of the first invoice of the list
def create_invoice(client, organization_id, contact_id, product_id, unit_price, amount, currency, date):
    invoice = {
        'organizationId': organization_id,
        'contactId': contact_id,
        'currencyId': currency,
        'entryDate': date[:10],
        'paymentTermsDays': 15,
        'state': 'approved',
        'sentState': 'sent',
        'lines': [{
            'productId': product_id,
            'unitPrice': unit_price,
            'quantity': amount
        }]
    }
    response = client.request('POST', '/invoices', {'invoice': invoice})

    return response['invoices'][0]['id']


def create_payment(client, organization_id, invoice_id, contact_id, bank_account_id, amount, currency, date, ):
    """
    Crazy messed up way to mark an invoice paid
    """
    payment = {
        'organizationId': organization_id,
        'contactId': contact_id,
        'subjectCurrencyId': currency,
        'entryDate': date[:10],
        'cashAmount': amount,
        'cashSide': 'debit',
        'cashAccountId': bank_account_id,
        "associations": [
            {
                "subjectReference": "invoice:{}".format(invoice_id)
            }
        ]
    }
    response = client.request('POST', '/bankPayments', {'bankPayment': payment})

    return response['invoices'][0]['id']


# Get id of organization associated with the API token.
def get_organization_id(client):
    response = client.request('GET', '/organization', None)

    return response['organization']['id']


# Gets a invoice by its Id
def get_invoice(client, invoice_id):
    response = client.request('GET', '/invoices', invoice_id)
    return response['invoice']


def save_invoice_pdf(client, invoice_id, destination):
    """
    Given an invoice ID, saves the PDF to a specific destination
    """
    response = client.request('GET', '/invoices', invoice_id)
    response = requests.get(response['invoice']['downloadUrl'], allow_redirects=True)
    open(destination, 'wb').write(response.content)


# Gets a invoice by its Id
def print_accounts(client):
    response = client.request('GET', '/accounts', None)

    for account in response['accounts']:
        print(account['name'], account['id'])


def print_products(client):
    response = client.request('GET', '/products', None)

    for product in response['products']:
        print(product['name'] + ", " + product['id'])
