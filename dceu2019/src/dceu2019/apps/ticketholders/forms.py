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


class NewsletterSignupForm(forms.ModelForm):

    def clean_email(self):
        email = self.cleaned_data.get('email', "")
        return email.lower()

    class Meta:
        model = models.Subscription
        fields = ('email',)
