# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bom_data_point',
            unique_together=set([('site', 'time')]),
        ),
        migrations.AlterUniqueTogether(
            name='pv_production_point',
            unique_together=set([('site', 'time')]),
        ),
        migrations.AlterUniqueTogether(
            name='site_weather_data',
            unique_together=set([('site', 'date')]),
        ),
    ]
