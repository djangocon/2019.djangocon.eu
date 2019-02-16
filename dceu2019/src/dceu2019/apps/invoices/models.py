from django.conf import settings
from django.db import models

from decimal import Decimal
from djmoney.models.fields import MoneyField


class BillyInvoiceContact(models.Model):
    """
    A contact created in Billy. The general case is that it's a company with a
    single contact person (created as a separate object in Billy)    
    """

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=12, choices=[
        ('company', 'company'),
        ('person', 'person')
    ])
    person_name = models.CharField(max_length=255, null=True)
    person_email = models.EmailField(max_length=255, null=True)
    person_id = models.CharField(max_length=12, null=True)
    country = models.CharField(max_length=3)
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
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )

    ticketbutler_orderid = models.CharField(max_length=16)

    billy_invoice_id = models.CharField(max_length=16)
    billy_product_id = models.CharField(max_length=16)
    billy_contact = models.ForeignKey(
        BillyInvoiceContact,
        on_delete=models.PROTECT,
    )

    created = models.DateTimeField(auto_now_add=True)
    when = models.DateTimeField()

    price = MoneyField(decimal_places=2, max_digits=14)
    vat = models.DecimalField(
        decimal_places=2,
        choices=(("0.00", Decimal(0.00)), ("0.25", Decimal(0.25))),
        default=Decimal(0.25),
        max_digits=6,
    )
    amount = models.SmallIntegerField(default=1)
    
    ticket_type_name = models.CharField(max_length=255)

    pdf = models.FileField()
