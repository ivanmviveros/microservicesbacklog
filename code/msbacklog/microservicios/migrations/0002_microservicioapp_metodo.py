# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-24 21:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microservicios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='microservicioapp',
            name='metodo',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]