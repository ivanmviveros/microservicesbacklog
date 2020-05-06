# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from historiasUsuario.models import Proyecto, HistoriaUsuario

# Create your models here.
class MetodoDescomposicion (models.Model):
    nombre = models.CharField(max_length=255)    
    descripcion = models.CharField(max_length=500, null= True)    

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre
    
    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class MicroservicioApp (models.Model):
    nombre = models.CharField(max_length=255)    
    descripcion = models.CharField(max_length=500, null= True)
    tiempo_estimado_desarrollo = models.FloatField(null= True)
    coupling = models.FloatField(null= True)
    cohesion = models.FloatField(null= True)
    avg_calls = models.FloatField(null= True)
    valor_GM = models.FloatField(null= True)    

    metodo = models.ForeignKey(MetodoDescomposicion, on_delete=models.PROTECT, null=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT, null=True)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre
    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class Microservicio (models.Model):
    nombre = models.CharField(max_length=255)    
    descripcion = models.CharField(max_length=500, null= True)
    numero_operaciones = models.IntegerField(null= True)
    numero_historias = models.IntegerField(null= True)
    total_puntos = models.IntegerField(null= True)
    tiempo_estimado_desarrollo = models.FloatField(null= True)
    complejidad_cognitiva = models.FloatField(null= True)
    
    aplicacion = models.ForeignKey(MicroservicioApp, on_delete=models.PROTECT, null = True)

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
    observaciones = models.CharField(max_length=255, null= True)

    microservicio = models.ForeignKey(Microservicio, on_delete=models.PROTECT, null = True)    

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class Microservicio_Historia (models.Model):
    microservicio = models.ForeignKey(Microservicio, on_delete=models.PROTECT)
    historia = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT)

    def __str__(self): # __unicode__ en Python 2 
        return self.microservicio.nombre + ' ' + self.historia.identificador

    class Meta:        
        ordering = ["microservicio"]
        default_permissions = ('add', 'change', 'delete', 'view')
