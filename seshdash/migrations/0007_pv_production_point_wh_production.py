# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0006_auto_20150727_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='pv_production_point',
            name='wh_production',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
