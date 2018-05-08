# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-05-08 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radmin', '0002_auto_20180508_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='policy',
            name='nPages',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
