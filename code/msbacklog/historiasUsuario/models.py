# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from microservicios import Microservicio

# Create your models here.
class Proyecto (models.Model):
    nombre = models.CharField(max_length=255)
    sigla = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=500)
    fecha_creacion = models.DateField(auto_now_add=True)
    es_publico = models.BooleanField(default= True)

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)

    def __str__(self): # __unicode__ en Python 2 
        return self.sigla

    class Meta:
        ordering = ["sigla"]
        default_permissions = ('add', 'change', 'delete', 'view')

class HistoriaUsuario (models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=500)
    prioridad = models.IntegerField()
    puntos_estimados = models.IntegerField()
    tiempo_estimado = models.FloatField()
    escenario = models.CharField(max_length=500)
    observaciones = models.CharField(max_length=500)
    fecha_creacion = models.DateField(auto_now_add=True)

    proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT)
    dependencias = models.ManyToManyField(HistoriaUsuario, through='Dependencia_Historia')
    microservicio = models.ForeignKey(Microservicio, on_delete=models.PROTECT, null=True)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class Dependencia_Historia(models.Model):
    historiaUsuario = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT)
    dependencia = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT)

class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    password = models.CharField(max_length=10)
    email = models.EmailField()
    direccion = models.TextField()
    telefono = models.CharField(max_length=12)


    


