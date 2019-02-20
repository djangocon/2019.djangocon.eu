from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from pretalx.person.models import User

from . import models


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = ('ticket_type_name', 'name', 'when', 'price',)

    def name(self, instance):
        return instance.billy_contact.name


@admin.register(models.BillyInvoiceContact)
class InvoiceContactAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TicketbutlerTicket)
class TicketbutlerTicketAdmin(admin.ModelAdmin):

    list_display = ['user', 'name', 'nick', 'sprints']
    list_filter = ['sprints']

    def name(self, instance):
        return instance.user.name

    def nick(self, instance):
        return instance.user.nick


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    This doesn't exist in PreTalx, but we probably need it...
    """
    ordering = None

    list_display = ['email', 'name', 'nick']
