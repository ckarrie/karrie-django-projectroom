# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-11-01 11:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projectroom', '0002_auto_20181101_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='request_at',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]