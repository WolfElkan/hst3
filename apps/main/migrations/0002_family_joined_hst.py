# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-12-05 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='joined_hst',
            field=models.DecimalField(decimal_places=0, default='1995', max_digits=4),
            preserve_default=False,
        ),
    ]
