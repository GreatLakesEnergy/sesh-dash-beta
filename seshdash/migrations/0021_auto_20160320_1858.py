# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-20 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0020_auto_20160317_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesh_site',
            name='vrm_site_id',
            field=models.CharField(blank=True, default=b'', max_length=20, null=True),
        ),
    ]
