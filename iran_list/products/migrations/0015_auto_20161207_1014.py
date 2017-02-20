# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_product_n_p_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='n_p_score',
            field=models.IntegerField(default=0, verbose_name='Net Promoter Score'),
        ),
    ]
