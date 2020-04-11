# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Microservicio (models.Model):
    nombre = models.CharField(max_length=255)    
    numero_operaciones = models.IntegerField()
    numero_historias = models.IntegerField()
    total_puntos = models.IntegerField()
    tiempo_estimado_desarrollo = models.FloatField()
    
    aplicacion = models.ForeignKey(MicroservicioApp, on_delete=models.PROTECT, null = True)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class MicroservicioApp (models.Model):
    nombre = models.CharField(max_length=255)    
    descripcion = models.CharField(max_length=500)
    tiempo_estimado_desarrollo = models.FloatField()
    coupling = models.FloatField()
    cohesion = models.FloatField()
    avg_calls = models.FloatField()
    valor_GM = models.FloatField()

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class Operacion (models.Model):
    nombre = models.CharField(max_length=255)    
    descripcion = models.CharField(max_length=500)
    url_identificacion = models.CharField(max_length=255)
    signatura = models.CharField(max_length=255)
    entrada = models.CharField(max_length=255)
    salida = models.CharField(max_length=255)

    microservicio = models.ForeignKey(Microservicio, on_delete=models.PROTECT, null = True)    

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

