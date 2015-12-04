# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bom_data_point',
            name='trans',
            field=models.IntegerField(default=0),
        ),
    ]
