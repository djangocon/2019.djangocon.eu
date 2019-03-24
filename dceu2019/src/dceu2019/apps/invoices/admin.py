from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from pretalx.person.models import User

from . import models


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    search_fields = ('name',)

    list_display = ('ticket_type_name', 'name', 'when', 'price', 'amount')

    def name(self, instance):
        return instance.billy_contact.name


@admin.register(models.BillyInvoiceContact)
class InvoiceContactAdmin(admin.ModelAdmin):
    search_fields = ('name', 'person_email',)
    list_display = ['name', 'person_email']


@admin.register(models.TicketbutlerTicket)
class TicketbutlerTicketAdmin(admin.ModelAdmin):

    search_fields = ('user__name', 'user__email')

    list_display = ['user', 'name', 'email', 'nick', 'sprints', 'logged_in', 'active', 'free_ticket']
    list_filter = ['sprints', 'user__is_active', 'free_ticket', 'ticketbutler_ticket_type_name']

    def name(self, instance):
        return instance.user.name

    def email(self, instance):
        return instance.user.email

    def nick(self, instance):
        return instance.user.nick

    def logged_in(self, instance):
        return instance.user.has_usable_password()
    logged_in.boolean = True

    def active(self, instance):
        return instance.user.is_active
    active.boolean = True


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

    change_form_template = 'loginas/change_form.html'
