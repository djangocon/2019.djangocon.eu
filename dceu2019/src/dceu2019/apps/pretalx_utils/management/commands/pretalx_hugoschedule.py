"""
 Prints CSV of all fields of a model.
"""
import json
import os

from django.core.management.base import BaseCommand
from pretalx.submission import models
from sorl.thumbnail import get_thumbnail

PUBLISHED = [
    "DG7SG8",
    "ZBYYMV",
    "GQKCWS",
    "WAHJMJ",
    "C3TXDX",
]


class Command(BaseCommand):
    help = ("Output all submissions as CSV (pipe to .csv file)")

    def handle(self, *args, **options):

        confirmed_talks = []

        for submission in models.Submission.objects.filter(state=models.SubmissionStates.CONFIRMED, code__in=PUBLISHED):

            speakers = list(submission.speakers.all())
            speaker_names = ", ".join([person.get_display_name() for person in speakers])

            images = {}

            for speaker in speakers:
                self.stdout.write(self.style.SUCCESS("Adding confirmed speaker {}".format(speaker.get_display_name())))
                if speaker.avatar:
                    im = get_thumbnail(speaker.avatar, '200x200', crop='center', quality=80)
                    images[speaker] = "https://members.2019.djangocon.eu" + im.url
                elif speaker.get_gravatar:
                    images[speaker] = "https://www.gravatar.com/avatar/" + speaker.gravatar_parameter
                else:
                    images[speaker] = None

            confirmed_talks.append(
                {
                    'title': submission.title,
                    'abstract': submission.abstract,
                    'speaker': speaker_names,
                    'speaker_image': images[speakers[0]]
                }
            )

        import dceu2019
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                dceu2019.__file__
            )))),
            "hugo_site",
            "data",
            "talks.json"
        )

        json.dump(
            confirmed_talks,
            open(json_path, "w")
        )
