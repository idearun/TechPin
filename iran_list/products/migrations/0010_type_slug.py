# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_auto_20161020_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='type',
            name='slug',
            field=models.SlugField(default='', verbose_name='Slug'),
            preserve_default=False,
        ),
    ]
