# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20161020_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='hits',
            field=models.IntegerField(default=0, verbose_name='Hits'),
        ),
    ]
