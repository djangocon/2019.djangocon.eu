from dceu2019.apps.invoices.models import TicketbutlerTicket
from django.contrib.auth.decorators import user_passes_test

REDIRECT_FIELD_NAME = 'next'


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):

    def test_user(user):
        return user.is_authenticated and (user.is_superuser or TicketbutlerTicket.objects.filter(user=user, refunded=False).exists())

    actual_decorator = user_passes_test(
        test_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
