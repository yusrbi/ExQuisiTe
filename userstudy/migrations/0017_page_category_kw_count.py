# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-27 08:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userstudy', '0016_auto_20171124_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='category_kw_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]