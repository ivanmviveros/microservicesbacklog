# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-05 04:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('microservicios', '0004_auto_20200505_0356'),
    ]

    operations = [
        migrations.AddField(
            model_name='microservicioapp',
            name='metodo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='microservicios.MetodoDescomposicion'),
        ),
    ]
