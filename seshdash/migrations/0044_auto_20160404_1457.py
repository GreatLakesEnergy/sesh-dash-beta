# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-04 12:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0043_auto_20160404_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rmc_status',
            name='rmc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
        migrations.AlterField(
            model_name='sesh_site',
            name='rmc_account',
            field=models.ForeignKey(blank=True, default=b'', max_length=20, null=True, on_delete=django.db.models.deletion.CASCADE, to='seshdash.Sesh_RMC_Account'),
        ),
        migrations.AlterField(
            model_name='sesh_user',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seshuser', to=settings.AUTH_USER_MODEL),
        ),
    ]