# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from microservicios.models import Microservicio, MicroservicioApp, Microservicio_Historia
import math

# Create your models here.
class Clasificacion (models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=500)    

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

class Metrica (models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=500)
    clase = models.ForeignKey(Clasificacion, on_delete=models.PROTECT)

    def __str__(self): # __unicode__ en Python 2 
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        default_permissions = ('add', 'change', 'delete', 'view')

    # Calcula el numero de puntos estimados del microservicio ms
    def calcularPuntosMicroservicio(self, ms):
        ms_historias = Microservicio_Historia.objects.filter(microservicio = ms)
        puntos =0
        if ms_historias:
            for ms_h in ms_historias:
                puntos += ms_h.historia.puntos_estimados
        return puntos
    
    # Calcula la métrica AIS y la cantidad de request o peticiones que le hacen al microservicio
    # devuelve un vector en el indice 0 está AIS y en el indice 1 está Request [AIS,Request]
    def calcularAisRequest(self, msCalcular, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)        
        if microservicios:
            clientes=0
            peticiones=0
            for ms in microservicios:
                valor=0
                if ms.id != msCalcular.id:
                    historias = Microservicio_Historia.objects.filter(microservicio = ms)
                    historiasmscal = Microservicio_Historia.objects.filter(microservicio = msCalcular)
                    for hu in historias:
                        dependencias = Dependencia_Historia.objects.filter(historia = hu)
                        for hums in historiasmscal:
                            if hums in dependencias:
                                valor+=1
                                peticiones+=1
                    if valor>0:
                        clientes += 1
        respuesta = [clientes, peticiones]
        return respuesta
    
    # Calcula la métrica ADS y la cantidad de calls o llamadas que hace el microservicio a otros
    # devuelve un vector en el indice 0 está ADS y en el indice 1 está Calls [ADS, Calls]
    def calcularAdsCalls(self, msCalcular, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)        
        if microservicios:
            clientes=0
            calls=0
            for ms in microservicios:
                valor=0
                if ms.id != msCalcular.id:
                    historias = Microservicio_Historia.objects.filter(microservicio = msCalcular)
                    historiasmscal = Microservicio_Historia.objects.filter(microservicio = ms)
                    for hu in historias:
                        dependencias = Dependencia_Historia.objects.filter(historia = hu)
                        for hums in historiasmscal:
                            if hums in dependencias:
                                valor+=1
                                calls+=1
                    if valor>0:
                        clientes += 1
        respuesta = [clientes, calls]
        return respuesta

    def calcularSiyLack (self, msCalcular, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)        
        interdependientes=0
        nointerdependientes=0
        if microservicios:
            for ms in microservicios:
                valor = 0
                valor2 = 0
                if ms.id != msCalcular.id:
                    historias = Microservicio_Historia.objects.filter(microservicio = ms)
                    historiasmscal = Microservicio_Historia.objects.filter(microservicio = msCalcular)
                    for hu in historiasmscal:
                        for hums in historias
                            dependencias = Dependencia_Historia.objects.filter(historia = hums)
                            if hu in dependencias:
                                valor+=1
                    if valor>0:
                        for hu in historias:
                            for hums in historiasmscal:
                                dependencias = Dependencia_Historia.objects.filter(historia = hums)
                                if hu in dependencias:
                                    valor2+=1
                    if valor>0 and valor2>0:
                        interdependientes+=1
                    else:
                        nointerdependientes+=1
        grado_cohesion = nointerdependientes / len(microservicios)
        respuesta = [interdependientes, nointerdependientes, grado_cohesion]
        return respuesta
    
    def calcularNumeroHistorias(self, msCalcular):
        ms_historias = Microservicio_Historia.objects.filter(microservicio = msCalcular)
        wsic = len(ms_historias)        
        return wsic
    
    def calcularTiempoDesarrollo(self, msCalcular):
        ms_historias = Microservicio_Historia.objects.filter(microservicio = msCalcular)
        tiempo =0.0
        if ms_historias:
            for ms_h in ms_historias:
                tiempo += ms_h.historia.tiempo_estimado
        return tiempo
    
    def calcularAcoplamiento(self, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)
        if microservicios:
            sumaais=0
            sumaads=0
            sumasiy=0
            for ms in microservicios:
                sumaais += ms.ais * ms.ais 
                sumaads += ms.ads * ms.ads
                sumasiy += ms.siy * ms.siy
            aist = math.sqrt(sumaais)
            adst = math.sqrt(sumaads)
            siyt = math.sqrt(sumasiy)
            cpt = math.sqrt( (aist*aist) + (adst*adst) + (siyt*siyt))
        respuesta = [aist, adst, siyt, cpt]
        return respuesta
    
    def calcularCohesion(self, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)
        if microservicios:
            sumacoh = 0
            for ms in microservicios:
                sumacoh += ms.grado_cohesion * ms.grado_cohesion 
            coht = math.sqrt(sumacoh)
        return coht
    
    def calcularWsicT(self, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)
        if microservicios:
            mayor = 0
            for ms in microservicios:
                if ms.numero_historias > mayor:
                    mayor = ms.numero_historias
        return mayor
    
    def calcularMetricaGranularidadGM(self, coht, cpt, wsict):
        gm = math.sqrt( (coht*coht) + (cpt*cpt) + (wsict*wsict) )
        return gm

    
