# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-12-08 22:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20171208_1618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='family',
            name='reg_status',
        ),
    ]
