from django.contrib import admin

from . import models


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BillyInvoiceContact)
class InvoiceContactAdmin(admin.ModelAdmin):
    pass
