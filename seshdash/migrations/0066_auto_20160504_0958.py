# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-04 07:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0065_auto_20160426_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesh_alert',
            name='point_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alert_rule',
            name='check_field',
            field=models.CharField(choices=[(b'BoM_Data_Point#battery_voltage', b'battery voltage'), (b'BoM_Data_Point#soc', b'System State of Charge'), (b'BoM_Data_Point#AC_output', b'AC Loads'), (b'BoM_Data_Point#pv_production', b'Solar Energy Produced'), (b'BoM_Data_Point#main_on', b'Grid Availible'), (b'BoM_Data_Point#genset_state', b'Generator on'), (b'RMC_status#minutes_last_contact', b'RMC Last Contact'), (b'battery_voltage', b'Battery Voltage in influx rule')], max_length=100),
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