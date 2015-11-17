# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert_Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=100)),
                ('value1', models.FloatField()),
                ('operator1', models.IntegerField()),
                ('field2', models.CharField(max_length=100)),
                ('value2', models.FloatField()),
                ('operator2', models.IntegerField()),
            ],
        ),
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
                ('pv_production', models.FloatField(default=0)),
                ('inverter_state', models.CharField(max_length=100)),
                ('genset_state', models.CharField(max_length=100)),
                ('relay_state', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Sesh_Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('isSilence', models.BooleanField()),
                ('alertSent', models.BooleanField()),
                ('alert', models.ForeignKey(to='seshdash.Alert_Rule')),
            ],
        ),
        migrations.CreateModel(
            name='Sesh_Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_name', models.CharField(max_length=100)),
                ('comission_date', models.DateTimeField(verbose_name=b'date comissioned')),
                ('location_city', models.CharField(max_length=100)),
                ('location_country', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('installed_kw', models.FloatField()),
                ('number_of_pv_strings', models.IntegerField()),
                ('Number_of_panels', models.IntegerField()),
                ('vrm_user_id', models.CharField(max_length=100)),
                ('vrm_password', models.CharField(max_length=100)),
                ('vrm_site_id', models.CharField(max_length=20)),
                ('battery_bank_capacity', models.IntegerField()),
                ('has_genset', models.BooleanField()),
                ('has_grid', models.BooleanField()),
            ],
            options={
                'permissions': (('view_Sesh_Site', 'View Sesh Site'),),
            },
        ),
        migrations.CreateModel(
            name='Sesh_User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('department', models.CharField(max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Site_Weather_Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(unique_for_date=True, verbose_name=b'date')),
                ('temp', models.IntegerField()),
                ('condition', models.CharField(max_length=20)),
                ('cloud_cover', models.FloatField()),
                ('sunrise', models.TimeField()),
                ('sunset', models.TimeField()),
                ('site', models.ForeignKey(to='seshdash.Sesh_Site')),
            ],
        ),
        migrations.AddField(
            model_name='sesh_alert',
            name='site',
            field=models.ForeignKey(to='seshdash.Sesh_Site'),
        ),
        migrations.AddField(
            model_name='bom_data_point',
            name='site',
            field=models.ForeignKey(to='seshdash.Sesh_Site'),
        ),
        migrations.AddField(
            model_name='alert_rule',
            name='site',
            field=models.ForeignKey(to='seshdash.Sesh_Site'),
        ),
        migrations.AddField(
            model_name='alert_rule',
            name='users',
            field=models.ForeignKey(to='seshdash.Sesh_User'),
        ),
        migrations.AlterUniqueTogether(
            name='site_weather_data',
            unique_together=set([('site', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='bom_data_point',
            unique_together=set([('site', 'time')]),
        ),
    ]
