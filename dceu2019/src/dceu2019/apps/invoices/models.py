from decimal import Decimal

from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField


class TicketbutlerTicket(models.Model):
    """
    Maps a ticketbutler ticket to a user

    We might wanna create users in the system that have access but don't have a
    ticket, and we don't want to fail our imports if a user already exists, then
    we might just have multiple tickets.

    The invoice says what type of ticket or how expensive it was etc.. but not
    really important, so we just store it there.

    This might at some point also start storing more information from
    Ticketbutler about food preferences etc. such that user can edit them
    later.

    Also: Sprints?
    """

    SPRINTS_NO = 0
    SPRINTS_MAYBE = 1
    SPRINTS_YES = 2

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE)
    ticketbutler_orderid = models.CharField(max_length=32, default="")
    invoice = models.ForeignKey("Invoice", null=True, blank=True, on_delete=models.SET_NULL)

    sprints = models.PositiveSmallIntegerField(
        choices=[(SPRINTS_NO, 'no'), (SPRINTS_MAYBE, 'maybe'), (SPRINTS_YES, 'yes')],
        null=True,
        blank=True,
    )

    @classmethod
    def get_or_create(cls, email, name, ticketbutler_orderid, sprints):
        """
        Creates a TicketbutlerTicket and possibly a disabled user account
        """

        # Need to import here, otherwise models fail to load
        from pretalx.person.models import User

        try:
            return TicketbutlerTicket.objects.get(user__email=email, ticketbutler_orderid=ticketbutler_orderid)
        except TicketbutlerTicket.DoesNotExist:
            pass

        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            user = User.objects.create_user(email=email.lower(), name=name)

        return TicketbutlerTicket.objects.create(
            user=user,
            ticketbutler_orderid=ticketbutler_orderid,
            sprints=sprints,
        )


class BillyInvoiceContact(models.Model):
    """
    A contact created in Billy. The general case is that it's a company with a
    single contact primary person (created as a separate object in Billy)
    """

    synced = models.BooleanField(default=False)
    billy_id = models.CharField(max_length=32, null=True)
    billy_person_id = models.CharField(max_length=32, null=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=12, choices=[
        ('company', 'company'),
        ('person', 'person')
    ])
    ticketbutler_orderid = models.CharField(max_length=32, default="")
    person_name = models.CharField(max_length=255, null=True)
    person_email = models.EmailField(max_length=255, null=True)
    person_id = models.CharField(max_length=32, null=True)
    country_code = models.CharField(max_length=3, default="DK")
    street = models.CharField(max_length=255, null=True)
    city_text = models.CharField(max_length=255, null=True)
    zipcode_text = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    registration_no = models.CharField(max_length=255, null=True)


class Invoice(models.Model):
    """
    Stores invoice data during import from Ticketbutler to Billy

    Note that not all users have invoices, and some might not even participate
    as attendees. This is why invoices for now are just a placeholder until
    we have API from Ticketbutler.
    """

    synced = models.BooleanField(default=False)
    ticketbutler_orderid = models.CharField(max_length=32)

    billy_id = models.CharField(max_length=32)
    billy_product_id = models.CharField(max_length=32)
    # Because Billy doesn't return an ID of a payment object
    billy_payment_created = models.BooleanField(default=False)
    billy_contact = models.ForeignKey(
        BillyInvoiceContact,
        on_delete=models.PROTECT,
    )

    created = models.DateTimeField(auto_now_add=True)
    when = models.DateTimeField()

    # Price w/o VAT
    price = MoneyField(decimal_places=2, max_digits=14)

    # Store the VAT as if it matters.. it's always 0.25 for Danish tickets to anyone
    vat = models.DecimalField(
        decimal_places=2,
        default=Decimal(0.25),
        max_digits=6,
    )

    # This is the *quantity*
    amount = models.SmallIntegerField(default=1)

    ticket_type_name = models.CharField(max_length=255)
