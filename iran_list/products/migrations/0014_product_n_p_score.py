# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_product_ranking'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='n_p_score',
            field=models.FloatField(default=0.0, verbose_name='Net Promoter Score'),
        ),
    ]
