import os

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.shortcuts import default as thumb_storage
from sorl.thumbnail.shortcuts import get_thumbnail

from . import models


@admin.register(models.TalkExtraProperties)
class TalkExtraProperties(admin.ModelAdmin):

    list_display = ("title", "speakers", "published", "twitter_card", "twitter_draft", "speaker_twitter_handle", "announced", "keynote", "workshop")
    list_editable = ("published", "keynote", "speaker_twitter_handle", "announced", "workshop")

    def title(self, instance):
        return instance.submission.title[:100]

    def twitter_draft(self, instance):
        return """Announcing {speaker}'s {type} "{title}" at #djangocon 🚲: {url}""".format(
            type="keynote" if instance.keynote else "workshop/break-out" if instance.workshop else "talk",
            speaker="@" + instance.speaker_twitter_handle if instance.speaker_twitter_handle else instance.speakers,
            title=instance.submission.title,
            url="https://2019.djangocon.eu/talks/" + instance.slug,
        )

    def twitter_card(self, instance):

        source = ImageFile(instance.twitter_card_image)
        path = thumb_storage.backend._get_thumbnail_filename(source, "300x200", {'format': 'PNG'})

        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(full_path):
            os.unlink(full_path)

        thumbnail = get_thumbnail(instance.twitter_card_image, "300x200", format="PNG")
        settings.THUMBNAIL_FORCE_OVERWRITE = False
        html = """<a href="{url}" target="_blank"><img src="{img}"></a>""".format(
            url=instance.twitter_card_image.url,
            img=thumbnail.url
        )
        return mark_safe(html)
    twitter_card.short_description = "Twitter card"
    twitter_card.allow_tags = True
