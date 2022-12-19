# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    password = models.CharField(max_length=10)
    email = models.EmailField()
    direccion = models.TextField()
    telefono = models.CharField(max_length=12)

    @classmethod
    def crear_primer_usuario(cls):
        if not cls.objects.count():
            cls.objects.create(
                    nombre="admin",
                    password="password",
                    email="a@a.es.es",
                    direccion="1",
                    telefono="1"
            )

class Proyecto (models.Model):
    nombre = models.CharField(max_length=255)
    sigla = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=500)
    fecha_creacion = models.DateField(auto_now_add=True)
    es_publico = models.BooleanField(default= True)
    idioma = models.CharField(max_length=5, null=True, default="es")

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)

    def __str__(self): # __unicode__ en Python 2 
        return self.sigla
    
    def getTotalPuntos(self):
        listaHu = HistoriaUsuario.objects.filter(proyecto=self)
        total=0
        for hu in listaHu:
            total += hu.puntos_estimados
        return total
    
    def getNumeroHistorias(self):
        total = HistoriaUsuario.objects.filter(proyecto=self).count()
        return total

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
    escenario = models.CharField(max_length=1000, null=True)
    observaciones = models.CharField(max_length=500, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)

    proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT)    

    def __str__(self): # __unicode__ en Python 2 
        return self.identificador

    class Meta:
        ordering = ["prioridad"]
        default_permissions = ('add', 'change', 'delete', 'view')

    def get_json(self, include_dependencies=True):
        PRIORIDADES = ['Very low', 'Low', 'Medium', 'High', 'Very high']
        return {
            "id": self.nombre,
            "name": self.descripcion,
            "actor": self.observaciones,
            "description": "",
            "priority": PRIORIDADES[self.prioridad-1] if self.prioridad-1 < len(PRIORIDADES) and self.prioridad-1 > 0 else "Very Low",
            "points": self.puntos_estimados,
            "estimated_time": self.tiempo_estimado,
            "dependencies": [] if not include_dependencies else [dependencia_historia.dependencia.get_json(dependencia_historia.dependencia != self and dependencia_historia.historia != self) for dependencia_historia in self.historia_usuario.all()],
            "project": self.proyecto.nombre
        }


class Dependencia_Historia(models.Model):
    historia = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT, related_name='historia_usuario',  
                                    db_column='historia_usuario')
    dependencia = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT, related_name='dependencia_historia',  
                                    db_column='dependencia_historia')
    
    def __str__(self): # __unicode__ en Python 2 
        return self.historia.identificador + ' ' + self.dependencia.identificador

    class Meta:        
        default_permissions = ('add', 'change', 'delete', 'view')
