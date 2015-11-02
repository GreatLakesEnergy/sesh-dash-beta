# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0002_auto_20150823_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesh_site',
            name='enphase_site_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sesh_site',
            name='vrm_site_id',
            field=models.CharField(default='aaa', max_length=20),
            preserve_default=False,
        ),
    ]
