from dceu2019.apps.pretalx_utils.models import TalkExtraProperties
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template import loader


class Command(BaseCommand):
    help = 'Invites speakers with a voucher code'

    def add_arguments(self, parser):
        parser.add_argument(
            '--re-invite',
            action='store_true',
            dest='reinvite',
            help='Send invite again',
        )

    def handle(self, *args, **options):

        talks = TalkExtraProperties.objects.exclude(ticket_voucher="")

        if not options['reinvite']:
            talks = talks.exclude(voucher_sent=True)

        invited = 0

        for talk in talks:

            for user in talk.submission.speakers.all():

                context = {
                    'name': user.name,
                    'voucher': talk.ticket_voucher,
                    'email': user.email,
                }

                body = loader.render_to_string("ticketholders/invite_speaker.txt", context)
                subject = "Ticket voucher for DjangoCon"

                subject = ''.join(subject.splitlines())

                email_message = EmailMultiAlternatives(subject, body, "robot@django-denmark.org", [user.email])

                email_message.send(fail_silently=False)

                if not talk.voucher_sent:
                    self.stdout.write(self.style.SUCCESS("Invited {}".format(user.email)))
                else:
                    self.stdout.write(self.style.SUCCESS("Re-invited {}".format(user.email)))

                talk.voucher_sent = True
                talk.save()

                invited += 1

        self.stdout.write(self.style.SUCCESS("Sent {} vouchers".format(invited)))
