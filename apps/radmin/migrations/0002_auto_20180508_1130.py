# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-05-08 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radmin', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='policy',
            name='nPages',
            field=models.PositiveIntegerField(),
        ),
    ]
