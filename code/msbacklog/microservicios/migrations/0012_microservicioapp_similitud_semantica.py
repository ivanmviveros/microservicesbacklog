# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-01 03:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microservicios', '0011_microservicioapp_complejidad_cognitiva'),
    ]

    operations = [
        migrations.AddField(
            model_name='microservicioapp',
            name='similitud_semantica',
            field=models.FloatField(null=True),
        ),
    ]