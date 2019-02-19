import requests
from django.conf import settings


class TicketbutlerClient:
    """
    Ticketbutler doesn't have an official API doc yet, so this is just an
    implementation of the 'get everything' interface
    """

    def request(self):

        url = settings.TICKETBUTLER_API

        try:

            response = requests.get(
                url,
                headers={
                    'Authorization': settings.TICKETBUTLER_TOKEN,
                },
            )

            status_code = response.status_code
            raw_body = response.text

            if status_code >= 400:
                raise requests.exceptions.RequestException(
                    '{}: {} failed with {:d} - {}'
                    .format('GET', url, status_code, raw_body)
                )

            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            raise e
