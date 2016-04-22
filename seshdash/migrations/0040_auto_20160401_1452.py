# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-01 12:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0039_auto_20160401_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesh_alert',
            name='point_model',
            field=models.CharField(default=b'BoM_Data_Point', max_length=40),
        ),
        migrations.AlterField(
            model_name='rmc_status',
            name='rmc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
        migrations.AlterField(
            model_name='sesh_site',
            name='rmc_account',
            field=models.ForeignKey(blank=True, default=b'', max_length=20, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
    ]