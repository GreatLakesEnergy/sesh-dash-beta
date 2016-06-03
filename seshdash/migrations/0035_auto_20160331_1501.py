# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-31 13:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0034_auto_20160331_1324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sesh_alert',
            name='model_point_name',
        ),
        migrations.AddField(
            model_name='bom_data_point',
            name='target_alert',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_Alert'),
        ),
        migrations.AddField(
            model_name='rmc_status',
            name='target_alert',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_Alert'),
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
