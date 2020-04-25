# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from microservicios.models import Microservicio

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    password = models.CharField(max_length=10)
    email = models.EmailField()
    direccion = models.TextField()
    telefono = models.CharField(max_length=12)

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
    identificador = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=500)
    prioridad = models.IntegerField()
    puntos_estimados = models.IntegerField()
    tiempo_estimado = models.FloatField()
    escenario = models.CharField(max_length=500, null=True)
    observaciones = models.CharField(max_length=500, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)

    proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT)
    microservicio = models.ForeignKey(Microservicio, on_delete=models.PROTECT, null=True)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["prioridad"]
        default_permissions = ('add', 'change', 'delete', 'view')

class Dependencia_Historia(models.Model):
    historia = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT, related_name='historia_usuario',  
                                    db_column='historia_usuario')
    dependencia = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT, related_name='dependencia_historia',  
                                    db_column='dependencia_historia')

class TipoProyecto (models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=500)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre
    
    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')
    


