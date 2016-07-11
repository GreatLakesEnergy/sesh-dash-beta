# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-08 07:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0002_auto_20160608_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site_Measurements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row1', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'soc', max_length=30)),
                ('row2', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'battery_voltage', max_length=30)),
                ('row3', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_output_absolute', max_length=30)),
                ('row4', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_Load_in', max_length=30)),
                ('row5', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_Load_out', max_length=30)),
                ('row6', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_Voltage_in', max_length=30)),
                ('row7', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_Voltage_out', max_length=30)),
                ('row8', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_input', max_length=30)),
                ('row9', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'AC_output', max_length=30)),
                ('row10', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=b'pv_production', max_length=30)),
                ('row11', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=0, max_length=30)),
                ('row12', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=0, max_length=30)),
                ('row13', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=0, max_length=30)),
                ('row14', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=0, max_length=30)),
                ('row15', models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans')], default=0, max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='daily_data_point',
            name='daily_pv_yield',
            field=models.FloatField(default=0, verbose_name=b'Daily PV Yield'),
        ),
    ]
