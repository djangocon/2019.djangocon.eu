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
        field_names = ["speakers"] + field_names
        writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
        writer.writerow(field_names)
        for instance in models.Submission.objects.all():
            writer.writerow(
                [", ".join([person.get_display_name() for person in instance.speakers.all()])] +
                [str(getattr(instance, f)).encode('utf-8') for f in field_names]
            )