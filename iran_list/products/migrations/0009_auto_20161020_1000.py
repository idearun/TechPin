# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20161020_0016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rate',
            options={'verbose_name': 'Rate', 'verbose_name_plural': 'Rates'},
        ),
        migrations.AddField(
            model_name='profile',
            name='user_point',
            field=models.PositiveIntegerField(default=0, verbose_name='User Points'),
        ),
    ]
