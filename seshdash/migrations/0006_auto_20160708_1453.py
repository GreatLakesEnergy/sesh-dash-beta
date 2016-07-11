# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-08 12:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0005_auto_20160708_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site_measurements',
            name='row1',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'soc', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row10',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'cloud_cover', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row2',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'battery_voltage', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row3',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_output_absolute', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row4',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_Load_in', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row5',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_Load_out', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row6',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_Voltage_in', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row7',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_Voltage_out', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row8',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_input', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='site_measurements',
            name='row9',
            field=models.CharField(choices=[(b'AC_Load_in', b'AC Load in'), (b'AC_Load_out', b'AC Load out'), (b'AC_Voltage_in', b'AC Voltage in'), (b'AC_Voltage_out', b'AC Voltage out'), (b'AC_input', b'AC input'), (b'AC_output', b'AC output'), (b'AC_output_absolute', b'AC output absolute'), (b'battery_voltage', b'Battery Voltage'), (b'genset_state', b'Genset state'), (b'main_on', b'Main on'), (b'pv_production', b'PV production'), (b'relay_state', b'Relay state'), (b'soc', b'State of Charge'), (b'trans', b'Trans'), (b'cloud_cover', b'Cloud Cover')], default=b'AC_output', max_length=30, null=True),
        ),
    ]