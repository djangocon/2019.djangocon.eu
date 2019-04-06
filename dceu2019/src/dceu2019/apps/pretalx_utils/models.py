import os
from io import BytesIO

import requests
from django.conf import settings
from django.db import models
from django.utils.text import wrap
from PIL import Image, ImageDraw, ImageFont
from sorl.thumbnail.shortcuts import get_thumbnail


def twitter_card_path(instance, __):

    relative_path = 'pretalx_utils/twitter_card_{}.png'.format(instance.submission.code)

    # Delete any existing image
    fullname = os.path.join(settings.MEDIA_ROOT, relative_path)

    container_dir = os.path.dirname(fullname)

    if not os.path.exists(container_dir):
        os.makedirs(container_dir)

    if os.path.exists(fullname):
        os.remove(fullname)
    return relative_path


class TalkExtraProperties(models.Model):

    submission = models.ForeignKey('submission.Submission', on_delete=models.CASCADE)

    slug = models.SlugField(null=True, blank=True)

    twitter_card_image = models.ImageField(
        upload_to=twitter_card_path,
        null=True, blank=True
    )

    speaker_twitter_handle = models.CharField(max_length=255, null=True, blank=True)

    keynote = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    announced = models.BooleanField(default=False)
    workshop = models.BooleanField(default=False)

    ticket_voucher = models.CharField(max_length=255, default="")
    voucher_sent = models.BooleanField(default=False)

    employer_attribution = models.CharField(null=True, blank=True, max_length=255)
    employer_url = models.URLField(null=True, blank=True)

    max_attendance = models.PositiveSmallIntegerField(default=None, null=True, blank=True, help_text="Max attendance (for workshops)")

    @property
    def speakers(self):
        return ", ".join([person.get_display_name() for person in self.submission.speakers.all()])

    def get_public_site_url(self):
        if settings.DEBUG:
            domain = "http://localhost:1313"
        else:
            domain = "https://2019.djangocon.eu"
        return domain + "/talks/" + self.slug

    def generate_images(self):
        """
        Creates images for promotion of the talk
        """

        speaker = self.submission.speakers.all()[0]

        if speaker.avatar:
            avatar = get_thumbnail(speaker.avatar, '160x160', crop='center', quality=80)
            avatar = Image.open(avatar.storage.path(avatar.name))
        elif speaker.get_gravatar:
            r = requests.get(
                "https://www.gravatar.com/avatar/" + speaker.gravatar_parameter,
                allow_redirects=True
            )
            if r.status_code == 200:
                avatar = Image.open(BytesIO(r.content))
                avatar = avatar.resize((160, 160), Image.ANTIALIAS)
            else:
                avatar = Image.new('RGBA', (160, 160), 0)
        else:
            avatar = Image.new('RGBA', (160, 160), 0)

        # Now turn the avatar circular

        bigsize = (avatar.size[0] * 3, avatar.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(avatar.size, Image.ANTIALIAS)
        avatar.putalpha(mask)

        data_dir = os.path.join(os.path.dirname(__file__), "some_banners")

        background = Image.open(
            os.path.join(data_dir, "some_twitter_card.png")
        )

        new_card = Image.new('RGBA', background.size, (0, 0, 0, 0))

        # Add the background
        new_card.paste(background, (0, 0))

        # Add the avatar
        new_card.paste(avatar, (58, 77), mask)

        # Write the speaker names
        draw = ImageDraw.Draw(new_card)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", "Poppins-SemiBold.ttf"), 56)

        offset = 60

        speaker_lines = wrap(self.speakers, 30).split("\n")
        for line in speaker_lines:
            draw.text((280, offset), line, (230, 28, 93), font=font)
            offset += 65

        font = ImageFont.truetype(os.path.join(data_dir, "fonts", "Poppins-SemiBold.ttf"), 56)

        title = self.submission.title
        if self.keynote:
            title = "Keynote: " + title

        title_lines = wrap(title, 30).split("\n")

        lines_available = 5 - len(speaker_lines)
        if len(title_lines) > lines_available:
            title_lines[lines_available - 1] += "..."

        if lines_available < 0:
            lines_available = 0

        for line in title_lines[:lines_available]:
            draw.text((280, offset), line, (255, 255, 255), font=font)
            offset += 65

        # Render it to screen
        # new_card.show()

        image_path = twitter_card_path(self, "blahblah.png")
        full_path = os.path.join(settings.MEDIA_ROOT, image_path)

        new_card.save(full_path, format='png')

        self.twitter_card_image = image_path
        self.save()
