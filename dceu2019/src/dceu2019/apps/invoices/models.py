from decimal import Decimal

from django.db import models
from djmoney.models.fields import MoneyField


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
    country_code = models.CharField(max_length=3)
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
        choices=(("0.00", Decimal(0.00)), ("0.25", Decimal(0.25))),
        default=Decimal(0.25),
        max_digits=6,
    )

    # This is the *quantity*
    amount = models.SmallIntegerField(default=1)

    ticket_type_name = models.CharField(max_length=255)

    pdf = models.FileField(null=True, blank=True,)
