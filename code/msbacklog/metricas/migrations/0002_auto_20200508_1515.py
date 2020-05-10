# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-08 15:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metricas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clasificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.CharField(max_length=500)),
            ],
            options={
                'ordering': ['nombre'],
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.RemoveField(
            model_name='metrica',
            name='microservicio',
        ),
        migrations.RemoveField(
            model_name='metrica',
            name='valor',
        ),
        migrations.AlterField(
            model_name='metrica',
            name='clase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='metricas.Clasificacion'),
        ),
    ]