# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-19 12:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0012_auto_20160719_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor_bmv',
            name='node_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='sensor_emonth',
            name='node_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='sensor_emontx',
            name='node_id',
            field=models.IntegerField(default=0),
        ),
    ]
