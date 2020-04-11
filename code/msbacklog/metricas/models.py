# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from microservicios import Microservicio

# Create your models here.
class Metrica (models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=500)
    valor = models.FloatField()
    clase = models.CharField(max_length=255)

    microservicio = models.ForeignKey(Microservicio, on_delete=models.PROTECT)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')