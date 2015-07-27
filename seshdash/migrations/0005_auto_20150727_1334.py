# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seshdash', '0004_auto_20150727_1309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sesh_site',
            options={'permissions': (('view_Sesh_Site', 'View Sesh Site'),)},
        ),
    ]
