# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PV_Production_Point',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('w_production', models.IntegerField()),
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
                ('longtude', models.FloatField()),
                ('installed_kw', models.IntegerField()),
                ('number_of_pv_strings', models.IntegerField()),
                ('Number_of_panels', models.IntegerField()),
                ('enphase_ID', models.CharField(max_length=100)),
                ('vrm_ID', models.CharField(max_length=100)),
                ('battery_bank_capactiy', models.IntegerField()),
                ('has_genset', models.BooleanField()),
                ('has_grid', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='pv_production_point',
            name='site',
            field=models.ForeignKey(to='seshdash.Sesh_Site'),
        ),
    ]
