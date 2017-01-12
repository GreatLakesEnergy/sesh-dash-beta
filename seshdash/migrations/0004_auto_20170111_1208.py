# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-01-11 10:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0003_auto_20161212_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report_Sent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('date', models.DateTimeField()),
                ('report_date', models.DateTimeField()),
                ('status', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('sent_to', django_mysql.models.JSONField(default=dict)),
            ],
        ),
        migrations.RenameModel(
            old_name='Report',
            new_name='Report_Job',
        ),
        migrations.AddField(
            model_name='report_sent',
            name='report_job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seshdash.Report_Job'),
        ),
    ]