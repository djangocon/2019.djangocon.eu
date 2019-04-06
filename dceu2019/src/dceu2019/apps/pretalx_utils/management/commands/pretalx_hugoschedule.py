import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify
from markdown import markdown
from pretalx.submission import models as submission_models
from sorl.thumbnail import get_thumbnail

from ... import models

# Escape things a bit differently here, because we don't want to double-escape the ampersands
_html_escapes = {
    ord('<'): '&lt;',
    ord('>'): '&gt;',
    ord('"'): '&quot;',
}


def escape(text):
    """
    Escape things for Hugo markdown-friendlyness
    """
    return str(text).translate(_html_escapes)


TALK_PAGE_HTML = """---
title: "{title}"
description: "{description}"
date: {talk_date}
speakers: {speaker}
speaker_image: {speaker_image}
speaker_twitter: "{speaker_twitter}"
employer_attribution: "{employer_attribution}"
employer_url: "{employer_url}"
draft: false
keynote: {keynote}
workshop: {workshop}
twitter_card: {twitter_card}
room: "{room}"
timeslot: "{timeslot}"
---
{talk_abstract}

{talk_description}"""


class Command(BaseCommand):
    help = ("Output all submissions as CSV (pipe to .csv file)")

    def handle(self, *args, **options):

        confirmed_keynotes = []
        confirmed_talks = []
        confirmed_workshops = []

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

        for submission in submission_models.Submission.objects.filter(state=submission_models.SubmissionStates.CONFIRMED):

            # Create extra properties
            props, __ = models.TalkExtraProperties.objects.get_or_create(submission=submission)

            props.generate_images()
            self.stdout.write(self.style.SUCCESS("Generated new SOME preview images"))

            if not props.slug:
                props.slug = slugify(submission.title)[:50]
                props.save()

            slug = props.slug

            speakers = list(submission.speakers.all())
            speaker_names = ", ".join([person.get_display_name() for person in speakers])

            images = {}

            if not props.published:
                self.stdout.write(self.style.WARNING("Skipping unpublished talk"))
                continue

            for speaker in speakers:
                self.stdout.write(self.style.SUCCESS("Adding confirmed speaker {}".format(speaker.get_display_name())))
                if speaker.avatar:
                    im = get_thumbnail(speaker.avatar, '200x200', crop='center', quality=80)
                    images[speaker] = "https://members.2019.djangocon.eu" + im.url
                elif speaker.get_gravatar:
                    images[speaker] = "https://www.gravatar.com/avatar/" + speaker.gravatar_parameter
                else:
                    images[speaker] = None

            submission_json = {
                'title': submission.title,
                'abstract': submission.abstract,
                'speakers': speaker_names,
                'speaker_image': images[speakers[0]],
                'slug': slug,
                'speaker_twitter': props.speaker_twitter_handle,
                'keynote': 1 if props.keynote else 0,
                'workshop': 1 if props.workshop else 0,
            }

            if props.keynote:
                confirmed_keynotes.append(submission_json)
            elif props.workshop:
                confirmed_workshops.append(submission_json)
            else:
                confirmed_talks.append(submission_json)

            with timezone.override("Europe/Copenhagen"):
                start_time = timezone.localtime(props.submission.slot.start).strftime("%A %H:%M")
                end_time = timezone.localtime(props.submission.slot.end).strftime("%H:%M")

            talk_detail_page_content = TALK_PAGE_HTML.format(
                title=escape(submission.title),
                description=escape(strip_tags(markdown(submission.abstract))),
                speaker=speaker_names,
                speaker_image=images[speakers[0]],
                talk_title=submission.title,
                talk_date=str(datetime.now()),
                talk_abstract=submission.abstract,
                talk_description=submission.description,
                speaker_twitter=props.speaker_twitter_handle or "",
                employer_attribution=props.employer_attribution or "",
                employer_url=props.employer_url or "",
                keynote='true' if props.keynote else 'false',
                workshop='true' if props.workshop else 'false',
                twitter_card='https://members.2019.djangocon.eu' + props.twitter_card_image.url,
                room=props.submission.slot.room,
                timeslot=start_time + "-" + end_time,
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

        json_path = os.path.join(
            hugo_site_path,
            "data",
            "keynotes.json"
        )

        json.dump(
            confirmed_keynotes,
            open(json_path, "w")
        )

        json_path = os.path.join(
            hugo_site_path,
            "data",
            "workshops.json"
        )

        json.dump(
            confirmed_workshops,
            open(json_path, "w")
        )
