from django.contrib import admin

from . import models


@admin.register(models.BicycleType)
class BicycleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_day')
