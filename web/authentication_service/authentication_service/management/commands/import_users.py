import csv

import datetime
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.timezone import UTC


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv_file")

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file) as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # skip header

            for row in reader:
                username = row[0].lower()
                password = row[1]
                joined = datetime.datetime.strptime(row[1], "%d-%m-%Y").replace(tzinfo=UTC())
                self.create_user(username, password, joined)

    def create_user(self, username, password, joined):
        User.objects.filter(username=username).delete()
        user = User.objects.create_user(username=username, password=password)
        user.date_joined = joined
        user.save()