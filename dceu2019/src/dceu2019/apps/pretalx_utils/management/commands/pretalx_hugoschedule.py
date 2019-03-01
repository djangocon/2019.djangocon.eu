"""
 Prints CSV of all fields of a model.
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.html import escape, strip_tags
from django.utils.text import slugify
from markdown import markdown
from pretalx.submission import models
from sorl.thumbnail import get_thumbnail

PUBLISHED = [
    "DG7SG8",
    "ZBYYMV",
    "GQKCWS",
    "WAHJMJ",
    "C3TXDX",
    "ERUAGC",
    "QC8SNF",
    "ATAANB",
]

TALK_PAGE_HTML = """---
title: "{title}"
description: "{description}"
date: {talk_date}
speakers: {speaker}
speaker_image: {speaker_image}
draft: false
---
{talk_abstract}

{talk_description}"""


class Command(BaseCommand):
    help = ("Output all submissions as CSV (pipe to .csv file)")

    def handle(self, *args, **options):

        confirmed_talks = []

        import dceu2019

        hugo_site_path = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            dceu2019.__file__
                        )
                    )
                )
            ),
            "hugo_site",
        )

        talk_details_pages_path = os.path.join(
            hugo_site_path,
            "content",
            "talks",
        )

        for submission in models.Submission.objects.filter(state=models.SubmissionStates.CONFIRMED, code__in=PUBLISHED):

            speakers = list(submission.speakers.all())
            speaker_names = ", ".join([person.get_display_name() for person in speakers])

            images = {}

            slug = slugify(submission.title)

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
                    'speakers': speaker_names,
                    'speaker_image': images[speakers[0]],
                    'slug': slug,
                }
            )

            talk_detail_page_content = TALK_PAGE_HTML.format(
                title=escape(submission.title),
                description=escape(strip_tags(markdown(submission.abstract))),
                speaker=speaker_names,
                speaker_image=images[speakers[0]],
                talk_title=submission.title,
                talk_date=str(datetime.now()),
                talk_abstract=submission.abstract,
                talk_description=submission.description,
            )

            talk_page_file = os.path.join(
                talk_details_pages_path,
                slug + ".md"
            )
            open(talk_page_file, "w").write(talk_detail_page_content)

        json_path = os.path.join(
            hugo_site_path,
            "data",
            "talks.json"
        )

        json.dump(
            confirmed_talks,
            open(json_path, "w")
        )
