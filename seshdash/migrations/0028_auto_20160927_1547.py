# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-27 13:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0027_sesh_user_organisation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesh_user',
            name='organisation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_Organisation'),
        ),
    ]
