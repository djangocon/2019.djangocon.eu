import datetime

from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField


class BicycleType(models.Model):

    name = models.CharField(max_length=255)
    price_per_day = MoneyField(
        decimal_places=2,
        max_digits=14,
        help_text="Not displayed to people right now, there is a table further down",
        default=0,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('price_per_day', 'name',)


class BicycleBooking(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmed = models.BooleanField(
        default=False,
        help_text="Check this field to confirm your intention to pick up a bike."
    )
    bicycle_type = models.ForeignKey(
        'BicycleType',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    size = models.CharField(
        max_length=255,
        choices=[
            ("small", "Small (your height <168 cm)"),
            ("medium", "Medium (your height 165-180cm)"),
            ("large", "Large (your height >178cm)"),
        ],
        default="medium",
    )
    frame_type = models.PositiveSmallIntegerField(
        choices=[
            (None, "Undecided"),
            (0, "Straight bar"),
            (1, "Step-through"),
        ],
        default=None,
        null=True,
        blank=True,
    )
    days = models.PositiveSmallIntegerField(
        default=3,
        choices=[
            (3, "3 days"),
            (4, "4 days"),
            (5, "5 days"),
            (6, "6 days"),
            (7, "1 week"),
            (8, "Over a week"),
        ]
    )
    from_date = models.DateField(default=datetime.date.today)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Email(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Used to send this email from CLI",
    )
    template_content = models.TextField()
    subject = models.CharField(max_length=255)

    newsletter = models.BooleanField(
        default=True,
        help_text="Creates an unsubscribe link for newsletter subscribers."
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    count = models.PositiveSmallIntegerField(default=0)

    first_time_send = models.DateTimeField(null=True, blank=True)

    recipients = models.ManyToManyField("Recipient", blank=True)

    def __str__(self):
        return self.subject


class Recipient(models.Model):
    """
    Creates a unique hash of a recipient when sending an email, but not actually
    an email address! So should be fine not to clean up.
    """

    email_hash = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class Newsletter(models.Model):
    """
    Who subscribes to the newsletter?

    Unsubscribe = DELETE!
    """

    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
