# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-19 17:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_resetpasswordcode'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
        migrations.AddField(
            model_name='type',
            name='fa_name',
            field=models.CharField(default='', max_length=50, verbose_name='Persian Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='name_en',
            field=models.CharField(max_length=50, verbose_name='English Name'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name_fa',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Persian Name'),
        ),
    ]
