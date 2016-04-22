# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-18 11:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0051_auto_20160412_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rmc_status',
            name='rmc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
        migrations.AlterField(
            model_name='sesh_site',
            name='position',
            field=geoposition.fields.GeopositionField(max_length=42),
        ),
        migrations.AlterField(
            model_name='sesh_site',
            name='rmc_account',
            field=models.ForeignKey(blank=True, default=b'', max_length=20, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
    ]