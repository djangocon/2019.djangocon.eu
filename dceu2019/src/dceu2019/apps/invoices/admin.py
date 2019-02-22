from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from pretalx.person.models import User

from . import models


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = ('ticket_type_name', 'name', 'when', 'price',)

    def name(self, instance):
        return instance.billy_contact.name


@admin.register(models.BillyInvoiceContact)
class InvoiceContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'person_email']


@admin.register(models.TicketbutlerTicket)
class TicketbutlerTicketAdmin(admin.ModelAdmin):

    list_display = ['user', 'name', 'email', 'nick', 'sprints']
    list_filter = ['sprints']

    def name(self, instance):
        return instance.user.name

    def email(self, instance):
        return instance.user.email

    def nick(self, instance):
        return instance.user.nick


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    This doesn't exist in PreTalx, but we probably need it...
    """
    ordering = None

    list_display = ['email', 'name', 'nick']

    search_fields = ['email', 'name', 'nick']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name', 'nick')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
