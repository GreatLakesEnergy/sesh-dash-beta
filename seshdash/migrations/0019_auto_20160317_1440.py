# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-17 12:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0018_auto_20160316_1647'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sesh_site',
            name='rmc_account',
        ),
        migrations.AddField(
            model_name='sesh_rmc_account',
            name='site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_Site'),
            preserve_default=False,
        ),
    ]