# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site_Weather_Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name=b'date')),
                ('temp', models.IntegerField()),
                ('uv_index', models.IntegerField()),
                ('condition', models.CharField(max_length=20)),
                ('site', models.ForeignKey(to='seshdash.Sesh_Site')),
            ],
        ),
    ]
