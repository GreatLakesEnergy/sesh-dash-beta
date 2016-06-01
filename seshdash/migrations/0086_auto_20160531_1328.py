# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-31 11:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0085_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status_Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row1', models.CharField(choices=[(b'battery_voltage', b'Battery Voltage'), (b'soc', b'State of Charge')], max_length=30)),
                ('row2', models.CharField(choices=[(b'battery_voltage', b'Battery Voltage'), (b'soc', b'State of Charge')], max_length=30)),
                ('row3', models.CharField(choices=[(b'battery_voltage', b'Battery Voltage'), (b'soc', b'State of Charge')], max_length=30)),
                ('row4', models.CharField(choices=[(b'battery_voltage', b'Battery Voltage'), (b'soc', b'State of Charge')], max_length=30)),
                ('row5', models.CharField(choices=[(b'battery_voltage', b'Battery Voltage'), (b'soc', b'State of Charge')], max_length=30)),
            ],
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
        migrations.AddField(
            model_name='sesh_site',
            name='status_card',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Status_Card'),
        ),
    ]
