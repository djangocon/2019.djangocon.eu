from django.contrib import admin

from . import models


@admin.register(models.BikeType)
class BikeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_day')
