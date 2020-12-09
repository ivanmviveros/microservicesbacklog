# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from historiasUsuario.models import Proyecto, HistoriaUsuario
from random import randint


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
    aist = models.FloatField(null= True)
    adst = models.FloatField(null= True)
    siyt = models.FloatField(null= True)

    cohesion = models.FloatField(null= True)
    wsict = models.FloatField(null= True)
    
    avg_calls = models.FloatField(null= True)
    avg_request = models.FloatField(null= True)
    valor_GM = models.FloatField(null= True)

    complejidad_cognitiva = models.FloatField(null= True)
    similitud_semantica = models.FloatField(null= True)   

    numero_microservicios = models.IntegerField(null= True)

    metodo = models.ForeignKey(MetodoDescomposicion, on_delete=models.PROTECT, null=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT, null=True)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre
    
    def getTotalCalls(self):
        calls=0
        microservicios = Microservicio.objects.filter(aplicacion = self)
        if microservicios:
            for ms in microservicios:
                calls += ms.calls        
        return calls
    
    def getDataMicroservicesBacklog(self, matrizCalls):
        microservicios = Microservicio.objects.filter(aplicacion = self)
        edjes=""
        nodos=""
        metricas=""
        i=1
        mayor_puntos=0

        if microservicios:
            for ms in microservicios:
                colorr= randint(0,(255))
                colorg= randint(0,(255))
                colorb= randint(0,(255))

                valor = ms.total_puntos

                nodos+= str(i) + "," +  ms.nombre + "," + str(colorr) + "," +  str(colorg) + "," +  str(colorb) + "," +str(valor) + "|"

                if ms.total_puntos > mayor_puntos:
                    mayor_puntos= ms.total_puntos
                
                listaHistorias = ms.getHistorias()

                metricas += str(i) + ","
                metricas += ms.nombre + ","
                metricas += str(ms.numero_historias) + ","

                for hu in listaHistorias:
                    metricas += hu.historia.identificador + " - " + hu.historia.nombre + ";"
                metricas+= ","
                metricas += str(ms.total_puntos) + "," 
                metricas += str(ms.ais) + ","
                metricas += str(ms.ads) + ","
                metricas += str(ms.siy) + ","
                metricas += str(ms.lack) + ","
                metricas += str(round(ms.grado_cohesion,2) )+ ","
                metricas += str(ms.calls) + ","
                metricas += str(ms.request) + ","
                metricas += str(round(ms.tiempo_estimado_desarrollo,2)) + ","
                metricas += str(ms.total_puntos) + ","
                if ms.similitud_semantica==None:
                    ms.similitud_semantica=0.00
                metricas += str(round(ms.similitud_semantica,2)) + ","
                metricas += "|"
                i+=1                                                            

            i=1            
            for dato in matrizCalls:
                j=1
                for callms in dato:                    
                    if callms[1] > 0:
                        for k in range(0, callms[1]):                            
                            edjes += str(i) + "," + str(j) + "|"
                    j += 1
                
                i += 1
        vector= [nodos, edjes, metricas]
        return vector

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
    similitud_semantica = models.FloatField(null= True)
    
    ais = models.FloatField(null= True)
    ads = models.FloatField(null= True)
    siy = models.FloatField(null= True)
    
    lack = models.FloatField(null= True)
    grado_cohesion = models.FloatField(null= True)
    
    calls = models.FloatField(null= True)
    request = models.FloatField(null= True)  
    
    aplicacion = models.ForeignKey(MicroservicioApp, on_delete=models.PROTECT, null = True)

    def __str__(self): # __unicode__ en Python 2   
        return self.nombre

    class Meta:
        ordering = ["nombre"] 
        default_permissions = ('add', 'change', 'delete', 'view')
    
    def getHistorias(self):
        historias = Microservicio_Historia.objects.filter(microservicio = self)
        return historias        

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
