from django import forms

from . import models
from ..invoices.models import TicketbutlerTicket


class BicycleBookingForm(forms.ModelForm):

    class Meta:
        model = models.BicycleBooking
        widgets = {
            'size': forms.widgets.RadioSelect
        }
        fields = ('bicycle_type', 'size', 'frame_type', 'from_date', 'days', 'confirmed')


class SprintsForm(forms.ModelForm):

    class Meta:
        model = TicketbutlerTicket
        widgets = {
            'size': forms.widgets.RadioSelect
        }
        fields = ('sprints',)
