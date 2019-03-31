import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.http.response import HttpResponse
from django.shortcuts import redirect, render_to_response, resolve_url
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from . import forms, models
from ..invoices.models import TicketbutlerTicket
from .decorators import login_required


class IndexView(TemplateView):
    template_name = 'ticketholders/index.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)


class CommunityView(TemplateView):
    template_name = 'ticketholders/community.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c['slack_invite_token'] = settings.SLACK_INVITE_TOKEN
        return c


# Create your views here.
class LoginView(LoginView):
    """
    Display the login form and handle the login action.
    """
    form_class = AuthenticationForm
    template_name = 'ticketholders/auth/login.html'


class PasswordResetView(PasswordResetView):
    email_template_name = 'ticketholders/auth/password_reset_email.html'
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    subject_template_name = 'ticketholders/auth/password_reset_subject.txt'
    success_url = reverse_lazy('ticketholders:password_reset_done')
    template_name = 'ticketholders/auth/password_reset_form.html'
    title = _('Password reset')


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'ticketholders/auth/password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('ticketholders:password_reset_complete')
    template_name = 'ticketholders/auth/password_reset_confirm.html'
    title = _('Enter new password')


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'ticketholders/auth/password_reset_complete.html'


class LogoutView(LogoutView):
    template_name = 'ticketholders/auth/logged_out.html'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        from loginas.utils import restore_original_login
        restore_original_login(request)
        return redirect('ticketholders:login')


class PasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('ticketholders:password_change_done')
    template_name = 'ticketholders/auth/password_change_form.html'


class PasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'ticketholders/auth/password_change_done.html'


class BikeBooking(UpdateView):
    """
    We don't try to manage several bookings per ticket holder. Even if they have
    friends or partners. This is a technical concern for now, but if someone
    wants to create a more granular set of CRUD views, that would be great!
    """

    template_name = 'ticketholders/bikes/booking.html'
    model = models.BicycleBooking
    form_class = forms.BicycleBookingForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        return models.BicycleBooking.objects.get_or_create(user=self.request.user)[0]

    def form_valid(self, form):
        messages.success(self.request, "Saved your booking")
        return UpdateView.form_valid(self, form)

    def get_success_url(self):
        return resolve_url('ticketholders:bike_booking')


class SprintsUpdate(UpdateView):
    """
    We don't try to manage several bookings per ticket holder. Even if they have
    friends or partners. This is a technical concern for now, but if someone
    wants to create a more granular set of CRUD views, that would be great!
    """

    template_name = 'ticketholders/sprints.html'
    model = TicketbutlerTicket
    form_class = forms.SprintsForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        return TicketbutlerTicket.objects.get_or_create(user=self.request.user)[0]

    def form_valid(self, form):
        messages.success(self.request, "Saved your attendance")
        return UpdateView.form_valid(self, form)

    def get_success_url(self):
        return resolve_url('ticketholders:sprints')


@csrf_exempt
def newsletter(request):

    context = {}

    if request.method == "POST":
        f = forms.NewsletterSignupForm(request.POST)
        email = request.POST.get('email', "")
        # Do not disclose if an email already exists, just say that it's been
        # subscribed.
        if not models.Subscription.objects.filter(email=email).exists():
            if f.is_valid():
                subscription = f.save()
                subscription.send_confirm()
        # We could confirmations again, but that would mean we have to deal
        # with DOS... so skipping this.
        return render_to_response("ticketholders/newsletter.html", context)

    return HttpResponse("I only do POST", status=405)


def get_subscribe_key(email):
    correct_key = hashlib.sha256()
    correct_key.update(email.encode())
    correct_key.update(settings.SECRET_UNSUBSCRIBE_KEY.encode())
    return correct_key.hexdigest()


def get_unsubscribe_key(email):
    correct_key = hashlib.sha256()
    correct_key.update(email.encode())
    correct_key.update(settings.SECRET_UNSUBSCRIBE_KEY.encode())
    return correct_key.hexdigest()


@csrf_exempt
def newsletter_unsubscribe(request, email, key):

    correct_key = get_unsubscribe_key(email)

    if correct_key == key:
        # Don't bother about being verbose, it can be used to brute force the
        # key *tinfoil*
        models.Subscription.objects.filter(email=email).delete()

    return render_to_response("ticketholders/newsletter_unsubscribed.html", {})


@csrf_exempt
def newsletter_confirm(request, email, key):

    correct_key = get_subscribe_key(email)

    if correct_key == key:
        # Don't bother about being verbose, it can be used to brute force the
        # key *tinfoil*
        models.Subscription.objects.filter(email=email).update(confirmed=True)

    return render_to_response("ticketholders/newsletter_confirmed.html", {})
