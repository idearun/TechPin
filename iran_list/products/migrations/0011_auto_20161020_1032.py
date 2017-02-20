# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_type_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug'),
        ),
    ]
