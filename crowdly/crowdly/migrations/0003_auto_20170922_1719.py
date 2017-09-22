# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 17:19
from __future__ import unicode_literals

import crowdly.helpers
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdly', '0002_auto_20170922_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', django_extensions.db.fields.ShortUUIDField(blank=True, editable=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('latitude', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
                ('longitude', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('owners', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(crowdly.helpers.ModelDiffMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='device',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='device',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='device',
            name='owners',
        ),
    ]
