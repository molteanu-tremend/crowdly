# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdly', '0009_locationowner_last_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationowner',
            name='mobile_uuid',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
