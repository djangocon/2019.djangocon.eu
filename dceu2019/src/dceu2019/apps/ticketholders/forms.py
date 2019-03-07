from django import forms

from . import models


class BicycleBookingForm(forms.ModelForm):

    class Meta:
        model = models.BicycleBooking
        widgets = {
            'size': forms.widgets.RadioSelect
        }
        fields = ('confirmed', 'bicycle_type', 'size', 'frame_type', 'from_date', 'days')
