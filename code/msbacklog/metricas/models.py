# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from microservicios.models import Microservicio, MicroservicioApp, Microservicio_Historia
from historiasUsuario.models import Dependencia_Historia, HistoriaUsuario
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
    def calcularAisRequest( self, msCalcular, msapp):
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
                        for hums in historiasmscal:
                            cont = Dependencia_Historia.objects.filter(historia = hu.historia, dependencia = hums.historia).count()
                            if cont>0:
                                valor+=1
                                peticiones+=1
                    if valor>0:
                        clientes += 1
        respuesta = [clientes, peticiones]
        return respuesta
    
    # Calcula la métrica ADS y la cantidad de calls o llamadas que hace el microservicio a otros
    # devuelve un vector en el indice 0 está ADS y en el indice 1 está Calls [ADS, Calls]
    def calcularAdsCalls( self, msCalcular, msapp):
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
                        for hums in historiasmscal:
                            cont = Dependencia_Historia.objects.filter(historia = hu.historia, dependencia = hums.historia).count()
                            if cont>0:
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
                        for hums in historias:                            
                            cont = Dependencia_Historia.objects.filter(historia = hums.historia, dependencia = hu.historia).count()
                            if cont>0:
                                valor+=1
                    if valor>0:
                        for hu in historias:
                            for hums in historiasmscal:                                
                                cont = Dependencia_Historia.objects.filter(historia = hums.historia, dependencia = hu.historia).count()
                                if cont>0:
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
    
    def calcularMetricas(self, msapp):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)

        if microservicios:
            sumacalls = 0.0
            sumarequest = 0.0
            mayor_tiempo=0
            for ms in microservicios:                

                # calcular las métricas del microservicio
                ms.total_puntos = self.calcularPuntosMicroservicio(ms)
                rta = self.calcularAisRequest(ms, msapp)
                ms.ais= rta[0]
                ms.request = rta[1]
                rta = self.calcularAdsCalls(ms, msapp)
                ms.ads = rta[0]
                ms.calls = rta[1]
                rta = self.calcularSiyLack(ms, msapp)
                ms.siy = rta[0]
                ms.lack = rta[1]
                ms.grado_cohesion = rta[2]
                ms.numero_historias = self.calcularNumeroHistorias(ms)
                ms.tiempo_estimado_desarrollo = self.calcularTiempoDesarrollo(ms)

                if ms.tiempo_estimado_desarrollo > mayor_tiempo:
                    mayor_tiempo = ms.tiempo_estimado_desarrollo

                sumacalls += ms.calls
                sumarequest += ms.request

                ms.save()
            datos = self.calcularAcoplamiento(msapp)
            msapp.aist = datos[0]
            msapp.adst = datos[1]
            msapp.siyt = datos[2]
            msapp.coupling = datos[3]

            msapp.cohesion = self.calcularCohesion(msapp)
            msapp.wsict = self.calcularWsicT(msapp)
            msapp.numero_microservicios = len(microservicios)

            msapp.tiempo_estimado_desarrollo = mayor_tiempo

            msapp.avg_calls = sumacalls /  msapp.numero_microservicios
            msapp.avg_request = sumarequest /  msapp.numero_microservicios

            msapp.valor_GM = self.calcularMetricaGranularidadGM(msapp.cohesion, msapp.coupling, msapp.wsict)
            msapp.save()