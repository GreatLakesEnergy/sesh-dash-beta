# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0005_auto_20150727_1334'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sesh_site',
            old_name='battery_bank_capactiy',
            new_name='battery_bank_capacity',
        ),
    ]
