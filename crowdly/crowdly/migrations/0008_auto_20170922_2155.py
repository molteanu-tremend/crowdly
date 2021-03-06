# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 21:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdly', '0007_remove_location_owners'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(default=b'gt', max_length=2)),
                ('threshold', models.IntegerField(default=0)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name=b'Created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crowdly.Location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='owners',
            field=models.ManyToManyField(blank=True, through='crowdly.LocationOwner', to=settings.AUTH_USER_MODEL),
        ),
    ]
