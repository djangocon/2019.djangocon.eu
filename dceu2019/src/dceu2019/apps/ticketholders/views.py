from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls.base import reverse_lazy
from django.utils.translation import gettext_lazy as _


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
