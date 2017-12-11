# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-12-10 04:10
from __future__ import unicode_literals

import apps.main.custom_fields
from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(max_length=50)),
                ('line2', models.CharField(max_length=50, null=True)),
                ('city', models.CharField(max_length=25, null=True)),
                ('state', models.CharField(max_length=2, null=True)),
                ('zipcode', models.DecimalField(decimal_places=4, max_digits=9)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last', models.CharField(max_length=30)),
                ('phone', apps.main.custom_fields.PhoneNumberField(decimal_places=0, max_digits=10)),
                ('email', models.EmailField(max_length=254)),
                ('mother_id', models.PositiveIntegerField(null=True)),
                ('father_id', models.PositiveIntegerField(null=True)),
                ('reg_status', models.PositiveSmallIntegerField(default=0)),
                ('joined_hst', models.DecimalField(decimal_places=0, max_digits=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('address', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='floop', to='main.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first', models.CharField(max_length=20)),
                ('family_id', models.PositiveIntegerField()),
                ('last', models.CharField(max_length=30, null=True)),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('alt_phone', apps.main.custom_fields.PhoneNumberField(decimal_places=0, max_digits=10, null=True)),
                ('alt_email', models.EmailField(max_length=254, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first', models.CharField(max_length=20)),
                ('middle', models.CharField(max_length=20, null=True)),
                ('last', models.CharField(max_length=30, null=True)),
                ('prefer', models.CharField(max_length=20, null=True)),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('birthday', models.DateField()),
                ('height', models.FloatField()),
                ('alt_phone', apps.main.custom_fields.PhoneNumberField(decimal_places=0, max_digits=10, null=True)),
                ('alt_email', models.EmailField(max_length=254, null=True)),
                ('tshirt', models.CharField(choices=[('YS', 'Youth Small'), ('YM', 'Youth Medium'), ('YL', 'Youth Large'), ('XS', 'Adult Extra Small'), ('AS', 'Adult Small'), ('AM', 'Adult Medium'), ('AL', 'Adult Large'), ('XL', 'Adult Extra Large'), ('2X', 'Adult 2XL'), ('3X', 'Adult 3XL')], max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Family')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('password', apps.main.custom_fields.BcryptField()),
                ('owner_type', django_mysql.models.EnumField(choices=[(b'Family', b'Family'), (b'Student', b'Student')], null=True)),
                ('owner_id', models.PositiveIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
