# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-11 08:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0014_auto_20160310_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sesh_alert',
            name='trigger_alert',
        ),
    ]
