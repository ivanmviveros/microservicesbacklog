# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-05 03:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('microservicios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metrica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.CharField(max_length=500)),
                ('valor', models.FloatField()),
                ('clase', models.CharField(max_length=255)),
                ('microservicio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='microservicios.Microservicio')),
            ],
            options={
                'ordering': ['nombre'],
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
    ]
