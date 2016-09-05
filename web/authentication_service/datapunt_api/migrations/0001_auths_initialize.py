# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import User

TEST_USER = 'testuser'
PASSWORD = settings.TEST_USER_PASSWORD


def create_test_user(apps, schema_editor):
    try:
        test_user = User.objects.filter(username=TEST_USER)[0]
    except IndexError:
        test_user = User.objects.create(username=TEST_USER)
        test_user.set_password(PASSWORD)
        test_user.save()


def roll_back(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(code=create_test_user, reverse_code=roll_back)
    ]
