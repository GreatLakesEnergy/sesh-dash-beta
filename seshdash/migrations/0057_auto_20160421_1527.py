# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-21 13:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0056_auto_20160421_1110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rmc_status',
            options={'verbose_name': 'RMC Status', 'verbose_name_plural': "RMC Status's"},
        ),
        migrations.AlterField(
            model_name='rmc_status',
            name='rmc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
        migrations.AlterField(
            model_name='sesh_site',
            name='rmc_account',
            field=models.ForeignKey(blank=True, default=b'', max_length=20, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
    ]
