import datetime

from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField


class BikeType(models.Model):

    name = models.CharField(max_length=255)
    price_per_day = MoneyField(
        decimal_places=2,
        max_digits=14,
        help_text="Not displayed to people right now, there is a table further down"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('price_per_day', 'name',)


class BicycleBooking(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmed = models.BooleanField(
        default=False,
        help_text="Please check or un-check this field so we can understand whether this booking is confirmed or not."
    )
    bike_type = models.ForeignKey(
        'BikeType',
        on_delete=models.CASCADE,
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
            (1, "Step-trough"),
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
            (7, "7 week"),
            (8, "Over a week"),
        ]
    )
    from_date = models.DateField(default=datetime.date.today)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
