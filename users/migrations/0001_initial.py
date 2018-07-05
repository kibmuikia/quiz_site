# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-17 20:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileModel',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('pic', models.ImageField(blank=True, default='', upload_to='users/uploads/account_pic/')),
                ('bio', models.TextField(blank=True, default='', max_length=140)),
            ],
        ),
    ]
