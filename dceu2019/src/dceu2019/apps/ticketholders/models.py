import datetime

from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField


class BikeType(models.Model):

    name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    price_per_day = MoneyField(decimal_places=2, max_digits=14)

    def __str__(self):
        return "{} - size: {} (Per day: {})".format(self.name, self.size, self.price_per_day)

    class Meta:
        ordering = ('price_per_day', 'name', 'size',)


class BicycleBooking(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmed = models.BooleanField(
        default=False,
        help_text="Please check or un-check this field so we can understand whether this booking is confirmed or not."
    )
    bike_type = models.ForeignKey('BikeType', on_delete=models.CASCADE, null=True, blank=True)
    days = models.PositiveSmallIntegerField(default=1)
    from_date = models.DateField(default=datetime.date.today)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
