# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-12-12 10:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0002_auto_20161115_1328'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vrm_account',
            options={'permissions': (('view_VRM_Accounts', 'View VRM Acccount'),), 'verbose_name': 'VRM Account', 'verbose_name_plural': 'VRM Accounts'},
        ),
    ]