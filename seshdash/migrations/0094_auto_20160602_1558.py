# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-02 13:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0093_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rmc_status',
            name='rmc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
    ]
