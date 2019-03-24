from django.contrib import admin

from . import models


@admin.register(models.BicycleType)
class BicycleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_day')


@admin.register(models.BicycleBooking)
class BicycleBookingAdmin(admin.ModelAdmin):

    list_filter = ('confirmed', 'modified', 'bicycle_type', 'days')

    list_display = ('email', 'confirmed', 'modified', 'bicycle_type', 'size', 'frame_type', 'from_date', 'days')

    def email(self, instance):
        return instance.user.email


@admin.register(models.EmailTemplate)
class EmailAdmin(admin.ModelAdmin):

    list_display = ('subject', 'name', 'count', 'first_time_send')


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    search_fields = ('email',)
    list_display = ('email', 'created',)
