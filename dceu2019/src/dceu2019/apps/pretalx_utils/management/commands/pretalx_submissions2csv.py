"""
 Prints CSV of all fields of a model.
"""

from django.core.management.base import BaseCommand
import csv
import sys


from pretalx.submission import models


class Command(BaseCommand):
    help = ("Output all submissions as CSV (pipe to .csv file)")

    def handle(self, *args, **options):

        field_names = [f.name for f in models.Submission._meta.fields]
        writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
        writer.writerow(
            ["speakers", "score"] +
            field_names
        )
        for instance in models.Submission.objects.all():
            values = []
            speakers = ", ".join([person.get_display_name() for person in instance.speakers.all()])
            score = instance.average_score
            values.append(speakers)
            values.append(score)
            for f in field_names:
                value = getattr(instance, f)
                if not isinstance(value, (int, float)):
                    values.append(str(value).encode('utf-8'))
                else:
                    values.append(value)
            writer.writerow(values)
