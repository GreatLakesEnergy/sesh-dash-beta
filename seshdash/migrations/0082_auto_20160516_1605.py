# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-16 14:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0081_auto_20160516_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slack_Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('is_alert_channel', models.BooleanField(default=True)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slack_channel', to='seshdash.Sesh_Organisation')),
            ],
        ),
        migrations.RemoveField(
            model_name='slack_alert_channel',
            name='organisation',
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
        migrations.DeleteModel(
            name='Slack_Alert_Channel',
        ),
    ]