from datetime import timedelta

from dceu2019.apps.ticketholders.views import PasswordResetView
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import datetime

from ... import models


class Command(BaseCommand):
    help = 'Invites all known ticket holders who have not been invited'

    def add_arguments(self, parser):
        parser.add_argument(
            '--re-invite',
            action='store_true',
            dest='reinvite',
            help='Also invite the ones who have not signed up',
        )

    def handle(self, *args, **options):

        tickets = models.TicketbutlerTicket.objects.all()

        if not options['reinvite']:
            tickets = tickets.filter(
                invited=False
            )
        else:
            tickets = tickets.filter(
                Q(invited_when__lte=datetime.now() - timedelta(days=2)) |
                Q(invited_when=None)
            )

        domain = '127.0.0.1:8000' if settings.DEBUG else 'members.2019.djangocon.eu'

        invited = 0

        for ticket in tickets:

            context = {
                'email': ticket.user.email,
                'domain': domain,
                'site_name': "members.2019.djangocon.eu",
                'uid': urlsafe_base64_encode(force_bytes(ticket.user.pk)).decode(),
                'user': ticket.user,
                'token': PasswordResetView.token_generator.make_token(ticket.user),
                'protocol': 'http' if settings.DEBUG else 'https',
            }

            if not ticket.invited:
                body = loader.render_to_string("ticketholders/auth/invite_email.txt", context)
                subject = "Welcome to DjangoCon Europe Ticket holder's area!"
            else:
                body = loader.render_to_string("ticketholders/auth/reinvite_email.txt", context)
                subject = "Re-invite to DjangoCon Europe Ticket holder's area"

            subject = ''.join(subject.splitlines())

            email_message = EmailMultiAlternatives(subject, body, "robot@django-denmark.org", [ticket.user.email])
            if PasswordResetView.html_email_template_name is not None:
                html_email = loader.render_to_string(PasswordResetView.html_email_template_name, context)
                email_message.attach_alternative(html_email, 'text/html')

            email_message.send(fail_silently=False)

            if not ticket.invited:
                self.stdout.write(self.style.SUCCESS("Invited {}".format(ticket.user.email)))
            else:
                self.stdout.write(self.style.SUCCESS("Re-invited {}".format(ticket.user.email)))

            ticket.invited = True
            ticket.invited_when = datetime.now()
            ticket.save()

            invited += 1

        self.stdout.write(self.style.SUCCESS("Invited {} new users".format(invited)))
