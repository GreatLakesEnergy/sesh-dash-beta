# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0002_auto_20150725_1934'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sesh_site',
            old_name='vrm_ID',
            new_name='vrm_password',
        ),
        migrations.AddField(
            model_name='sesh_site',
            name='vrm_user_id',
            field=models.CharField(default=datetime.datetime(2015, 7, 27, 7, 14, 49, 272482, tzinfo=utc), max_length=100),
            preserve_default=False,
        ),
    ]
