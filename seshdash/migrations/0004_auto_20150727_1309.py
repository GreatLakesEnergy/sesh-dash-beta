# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0003_auto_20150727_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesh_site',
            name='installed_kw',
            field=models.FloatField(),
        ),
    ]
