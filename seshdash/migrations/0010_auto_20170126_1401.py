# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-01-26 12:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0009_merge'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='report_job',
            unique_together=set([('site', 'duration')]),
        ),
    ]
