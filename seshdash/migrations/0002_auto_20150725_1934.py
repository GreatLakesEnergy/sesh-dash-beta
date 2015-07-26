# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoM_Data_Point',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('soc', models.FloatField()),
                ('battery_voltage', models.FloatField()),
                ('AC_input', models.FloatField()),
                ('AC_output', models.FloatField()),
                ('AC_Load_in', models.FloatField()),
                ('AC_Load_out', models.FloatField()),
                ('inverter_state', models.CharField(max_length=100)),
                ('genset_state', models.CharField(max_length=100)),
                ('relay_state', models.CharField(max_length=100)),
                ('site', models.ForeignKey(to='seshdash.Sesh_Site')),
            ],
        ),
        migrations.AlterField(
            model_name='site_weather_data',
            name='date',
            field=models.DateTimeField(unique_for_date=True, verbose_name=b'date'),
        ),
    ]
