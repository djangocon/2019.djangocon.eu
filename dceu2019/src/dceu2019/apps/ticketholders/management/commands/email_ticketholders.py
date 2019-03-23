from dceu2019.apps.ticketholders.views import PasswordResetView
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.template import Template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pretalx.person.models import User

from ... import models


class Command(BaseCommand):
    help = 'Mandatory emails to ticket holders, contain no unsubscribe option'

    def add_arguments(self, parser):
        parser.add_argument('email_name', type=str)
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help="Email any user, also the ones who did not yet register or don't have tickets (includes speakers not with a ticket yet)",
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            help="Resets all before sending (force resend)",
        )

    def handle(self, *args, **options):

        try:
            email = models.Email.objects.get(name=options['email_name'])
        except models.Email.DoesNotExist:
            raise CommandError("Email '{}' not found".format(options['email_name']))

        users = User.objects.filter(is_active=True)

        if options['reset']:
            email.recipients.all().delete()

        if not options['all']:
            users = users.exclude(tickets=None)

        users = users.exclude(id__in=[u.id for u in email.recipients.all()])

        domain = '127.0.0.1:8000' if settings.DEBUG else 'members.2019.djangocon.eu'

        sent = 0

        for user in users:

            context = {
                'email': user.email,
                'domain': domain,
                'site_name': "members.2019.djangocon.eu",
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': PasswordResetView.token_generator.make_token(user),
                'protocol': 'http' if settings.DEBUG else 'https',
                'name': user.name,
            }
            body_template = Template(email.template_content)
            body = body_template(context)
            subject = email.subject
            subject = ''.join(subject.splitlines())

            email_message = EmailMultiAlternatives(subject, body, "robot@django-denmark.org", [user.email])

            email_message.send(fail_silently=False)

            email.recipients.add(user)

            sent += 1

        self.stdout.write(self.style.SUCCESS("Sent to {} new users".format(sent)))
