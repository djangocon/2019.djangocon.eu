import datetime

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.db import models
from django.template import Template
from django.template.context import Context
from djmoney.models.fields import MoneyField


class BicycleType(models.Model):

    name = models.CharField(max_length=255)
    price_per_day = MoneyField(
        decimal_places=2,
        max_digits=14,
        help_text="Not displayed to people right now, there is a table further down",
        default=0,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('price_per_day', 'name',)


class BicycleBooking(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmed = models.BooleanField(
        default=False,
        help_text="Check this field to confirm your intention to pick up a bike."
    )
    bicycle_type = models.ForeignKey(
        'BicycleType',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    size = models.CharField(
        max_length=255,
        choices=[
            ("small", "Small (your height <168 cm)"),
            ("medium", "Medium (your height 165-180cm)"),
            ("large", "Large (your height >178cm)"),
        ],
        default="medium",
    )
    frame_type = models.PositiveSmallIntegerField(
        choices=[
            (None, "Undecided"),
            (0, "Straight bar"),
            (1, "Step-through"),
        ],
        default=None,
        null=True,
        blank=True,
    )
    days = models.PositiveSmallIntegerField(
        default=3,
        choices=[
            (3, "3 days"),
            (4, "4 days"),
            (5, "5 days"),
            (6, "6 days"),
            (7, "1 week"),
            (8, "Over a week"),
        ]
    )
    from_date = models.DateField(default=datetime.date.today)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class EmailTemplate(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Used to send this email from CLI",
    )
    template_content = models.TextField(
        help_text="Unsubscribe links are automatically added at the bottom. Remember to add a good footer, and start it with '--' and linebreak",
    )
    subject = models.CharField(max_length=255)

    newsletter = models.BooleanField(
        default=True,
        help_text="Creates an unsubscribe link for newsletter subscribers."
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    count = models.PositiveSmallIntegerField(default=0)

    first_time_send = models.DateTimeField(null=True, blank=True)

    def populate_recipients(self, emails):
        for email in emails:
            Recipient.objects.get_or_create(
                email_template=self,
                email=email,
            )

    def mark_sent(self, email):
        Recipient.objects.filter(email_template=self, email=email).update(
            sent=True,
        )

    def send(self, recipient, unsubscribe=False):
        from dceu2019.apps.ticketholders.views import get_unsubscribe_key

        domain = '127.0.0.1:8000' if settings.DEBUG else 'members.2019.djangocon.eu'

        email = recipient.email

        context = {
            'email': recipient.email,
            'domain': domain,
            'site_name': domain,
            'protocol': 'http' if settings.DEBUG else 'https',
            'unsubscribe_key': get_unsubscribe_key(email),
        }

        body_template_source = self.template_content

        if unsubscribe:
            body_template_source += (
                "\n" +
                "\n" +
                "Unsubscribe:\n{{ protocol }}://{{ site_name }}{% url 'newsletter_unsubscribe' email=email key=unsubscribe_key %}"
            )
        else:
            body_template_source += (
                "\n\n" +
                "You are receiving this email because you have a ticket to DjangoCon Europe 2019 or a user account on the members' website."
            )

        body = Template(body_template_source).render(Context(context))

        subject = self.subject
        subject = ''.join(subject.splitlines())

        email_message = EmailMultiAlternatives(subject, body, "robot@django-denmark.org", [email])

        email_message.send(fail_silently=False)

        self.mark_sent(email)

    def __str__(self):
        return self.subject


class Recipient(models.Model):
    """
    Creates a unique hash of a recipient when sending an email, but not actually
    an email address. So should be fine not to clean up.
    """

    email_template = models.ForeignKey("EmailTemplate", related_name="recipients", on_delete=models.CASCADE)
    email = models.EmailField()
    sent = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("email_template", "email")


class Subscription(models.Model):
    """
    Who subscribes to the newsletter?

    Unsubscribe = DELETE!
    """

    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def send_confirm(self):
        from dceu2019.apps.ticketholders.views import get_subscribe_key

        domain = '127.0.0.1:8000' if settings.DEBUG else 'members.2019.djangocon.eu'

        context = {
            'email': self.email,
            'domain': domain,
            'site_name': domain,
            'protocol': 'http' if settings.DEBUG else 'https',
            'subscribe_key': get_subscribe_key(self.email),
        }

        body_template_source = (
            "You or someone else has asked you to subscribe to our newsletter."
            "\n" +
            "\n" +
            "Confirm your subscription:\n{{ protocol }}://{{ site_name }}{% url 'newsletter_confirm' email=email key=subscribe_key %}" +
            "\n" +
            "\n" +
            "Ignore this email and you won't be subscribed." +
            "\n" +
            "\n" +
            "--\n"
            "{{ protocol }}://{{ site_name }}"
        )

        body = Template(body_template_source).render(Context(context))
        subject = "Confirm your subscription to DjangoCon Europe 2019 newsletter"

        email_message = EmailMultiAlternatives(subject, body, "robot@django-denmark.org", [self.email])
        email_message.send(fail_silently=False)
