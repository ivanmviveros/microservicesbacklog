# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-08 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microservicios', '0008_operacion_observaciones'),
    ]

    operations = [
        migrations.AddField(
            model_name='microservicio',
            name='ads',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicio',
            name='ais',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicio',
            name='calls',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicio',
            name='grado_cohesion',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicio',
            name='lack',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicio',
            name='request',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicio',
            name='siy',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicioapp',
            name='adst',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicioapp',
            name='aist',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicioapp',
            name='avg_request',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicioapp',
            name='numero_microservicios',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='microservicioapp',
            name='siyt',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='microservicioapp',
            name='wsict',
            field=models.FloatField(null=True),
        ),
    ]
