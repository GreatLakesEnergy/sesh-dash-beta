# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-01 08:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0086_auto_20160531_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status_card',
            name='row4',
        ),
        migrations.RemoveField(
            model_name='status_card',
            name='row5',
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
        migrations.AlterField(
            model_name='status_card',
            name='row1',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'soc', max_length=30),
        ),
        migrations.AlterField(
            model_name='status_card',
            name='row2',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'battery_voltage', max_length=30),
        ),
        migrations.AlterField(
            model_name='status_card',
            name='row3',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_output_absolute', max_length=30),
        ),
    ]
