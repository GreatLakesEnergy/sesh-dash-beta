# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-17 11:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0016_auto_20160726_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor_Mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_id', models.IntegerField()),
                ('node_id', models.IntegerField()),
                ('sensor_type', models.CharField(max_length=40)),
            ],
        ),
    ]
