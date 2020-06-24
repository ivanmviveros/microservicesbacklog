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

    def calcularPuntosMicroservicio(self, ms):
        ms_historias = Microservicio_Historia.objects.filter(microservicio = ms)
        puntos =0
        if ms_historias:
            for ms_h in ms_historias:
                puntos += ms_h.historia.puntos_estimados
        return puntos
    
    # Calcula la métrica AIS y la cantidad de request o peticiones que le hacen al microservicio
    # devuelve un vector en el indice 0 está AIS y en el indice 1 está Request [AIS,Request]
    def calcularAisRequestIndividuo( self, msCalcular, microservicios):                
        if microservicios:
            clientes=0
            peticiones=0
            for ms in microservicios:
                valor=0
                if ms[0] != msCalcular[0]:
                    historias = ms[1]
                    historiasmscal = msCalcular[1]
                    for hu in historias:                        
                        for hums in historiasmscal:
                            cont = Dependencia_Historia.objects.filter(historia = hu, dependencia = hums).count()
                            if cont>0:
                                valor+=1
                                peticiones+=1
                    if valor>0:
                        clientes += 1
        respuesta = [clientes, peticiones]
        return respuesta
    
    # Calcula la métrica ADS y la cantidad de calls o llamadas que hace el microservicio a otros
    # devuelve un vector en el indice 0 está ADS y en el indice 1 está Calls [ADS, Calls]
    def calcularAdsCallsIndividuo( self, msCalcular, microservicios):        
        if microservicios:
            clientes=0
            calls=0
            for ms in microservicios:
                valor=0
                if ms[0] != msCalcular[0]:
                    historias = msCalcular[1]
                    historiasmscal = ms[1]
                    for hu in historias:                        
                        for hums in historiasmscal:
                            cont = Dependencia_Historia.objects.filter(historia = hu, dependencia = hums).count()
                            if cont>0:
                                valor+=1
                                calls+=1
                    if valor>0:
                        clientes += 1
        respuesta = [clientes, calls]
        return respuesta

    def calcularSiyLackIndividuo (self, msCalcular, microservicios):        
        interdependientes=0
        nointerdependientes=0
        if microservicios:
            for ms in microservicios:
                valor = 0
                valor2 = 0
                if ms[0] != msCalcular[0]:
                    historias = ms[1]
                    historiasmscal = msCalcular[1]
                    for hu in historiasmscal:
                        for hums in historias:                            
                            cont = Dependencia_Historia.objects.filter(historia = hums, dependencia = hu).count()
                            if cont>0:
                                valor+=1
                    if valor>0:
                        for hu in historias:
                            for hums in historiasmscal:                                
                                cont = Dependencia_Historia.objects.filter(historia = hums, dependencia = hu).count()
                                if cont>0:
                                    valor2+=1
                    if valor>0 and valor2>0:
                        interdependientes+=1
                    else:
                        nointerdependientes+=1
        grado_cohesion = nointerdependientes / len(microservicios)
        respuesta = [interdependientes, nointerdependientes, grado_cohesion]
        return respuesta
    
    def calcularNumeroHistoriasIndividuo(self, msCalcular):        
        wsic = len(msCalcular[1])        
        return wsic
    
    def calcularTiempoDesarrolloIndividuo(self, msCalcular):        
        tiempo =0.0
        if msCalcular[1]:
            for hu in msCalcular[1]:
                tiempo += hu.tiempo_estimado
        return tiempo
    
    def calcularAcoplamientoIndividuo(self, microservicios):        
        if microservicios:
            sumaais=0
            sumaads=0
            sumasiy=0
            for datos in microservicios:
                ms = datos[0]
                sumaais += ms.ais * ms.ais 
                sumaads += ms.ads * ms.ads
                sumasiy += ms.siy * ms.siy
            aist = math.sqrt(sumaais)
            adst = math.sqrt(sumaads)
            siyt = math.sqrt(sumasiy)
            cpt = math.sqrt( (aist*aist) + (adst*adst) + (siyt*siyt))
        respuesta = [aist, adst, siyt, cpt]
        return respuesta
    
    def calcularCohesionIndividuo(self, microservicios):        
        if microservicios:
            sumacoh = 0
            for datos in microservicios:
                ms = datos[0]
                sumacoh += ms.grado_cohesion * ms.grado_cohesion 
            coht = math.sqrt(sumacoh)
        return coht
    
    def calcularWsicTIndividuo(self, microservicios):        
        if microservicios:
            mayor = 0
            for datos in microservicios:
                ms = datos[0]
                if ms.numero_historias > mayor:
                    mayor = ms.numero_historias
        return mayor
    
    def calcularGMIndividuo(self, variables, microservicios):
        coht=0
        copt=0
        wsict=0
        cplt=0
        semant=0
        
        if variables:
            for var in variables:
                if var=="coupling":
                    rta = self.calcularAcoplamientoIndividuo(microservicios)
                    copt = rta[3]
                if var=="cohesion":
                    coht = self.calcularCohesionIndividuo(microservicios)
                if var=="complexity":
                    cplt = 0 # Falta crear el método de calcular la complejidad cognitiva de la MSApp
                if var=="wsict":
                    wsict = self.calcularWsicTIndividuo(microservicios)
                if var=="semantic":
                    semant = 0 # Falta crear el método de calcular la similitud semantica de la MSApp

        gm = math.sqrt( (coht*coht) + (copt*copt) + (wsict*wsict) + (cplt*cplt) + (semant*semant) )
        return gm
    
    def calcularPuntosMSIndividuo(self, fila):
        
        ms_historias = fila[1]
        puntos =0
        if ms_historias:
            for hu in ms_historias:
                puntos += hu.puntos_estimados
        return puntos
    
    def calcularMetricasIndividuo(self, microservicios, variables, dependencias):        
        if microservicios:
            sumacalls = 0.0
            sumarequest = 0.0
            mayor_tiempo=0
            listaMS=[]
            sumacuaAIS=0
            sumacuaADS=0
            sumacuaSIY=0
            sucmacuaCoh=0
            mayor_wsic=0
            mayor_puntos=0
            n= len(microservicios)
            contadorMS=0

            for dato in microservicios:                
                contadorMS += 1
                nombreMS = dato[0]

                ms = Microservicio(nombre= nombreMS)

                # calcular las métricas del microservicio
                rta = self.calcularMetricasMicroservicio(dato, microservicios, n, dependencias)

                ms.ais= rta[0]
                ms.request = rta[1]
                ms.ads = rta[2]
                ms.calls = rta[3]            
                ms.siy = rta[4]
                ms.lack = rta[5]
                ms.grado_cohesion = rta[6]
                ms.numero_historias = rta[7]
                ms.tiempo_estimado_desarrollo = rta[8]
                ms.total_puntos = rta[9]                                                                

                if ms.tiempo_estimado_desarrollo > mayor_tiempo:
                    mayor_tiempo = ms.tiempo_estimado_desarrollo

                sumacalls += ms.calls
                sumarequest += ms.request

                sumacuaAIS += ms.ais * ms.ais
                sumacuaADS += ms.ads * ms.ads
                sumacuaSIY += ms.siy * ms.siy

                sucmacuaCoh += ms.grado_cohesion * ms.grado_cohesion

                if ms.numero_historias > mayor_wsic:
                    mayor_wsic = ms.numero_historias
                
                if ms.total_puntos > mayor_puntos:
                    mayor_puntos = ms.total_puntos

                vector= [ms, dato[1]]
                listaMS.append(vector)            

            cua_coht=0
            cua_copt=0
            cua_wsict=0
            cua_cplt=0
            cua_semant=0

            aist = math.sqrt(sumacuaAIS)
            adst = math.sqrt(sumacuaADS)
            siyt = math.sqrt(sumacuaSIY)
            cpt = math.sqrt( (aist*aist) + (adst*adst) + (siyt*siyt))

            coht = math.sqrt(sucmacuaCoh)

            wsict=mayor_wsic
            cplt=mayor_puntos
            semant=0
            
            if variables:
                for var in variables:
                    if var=="coupling":                    
                        cua_copt = cpt * cpt 
                    if var=="cohesion":
                        cua_coht = coht * coht
                    if var=="complexity":
                        cua_cplt = cplt * cplt # Falta crear el método de calcular la complejidad cognitiva de la MSApp, toma mayor puntos
                    if var=="wsict":
                        cua_wsict = wsict * wsict
                    if var=="semantic":
                        cua_semant = semant * semant # Falta crear el método de calcular la similitud semantica de la MSApp

            gm = math.sqrt( (cua_coht) + (cua_copt) + (cua_wsict) + (cua_cplt) + (cua_semant) )

            msapp = MicroservicioApp()            
            msapp.aist = aist
            msapp.adst = adst
            msapp.siyt = siyt
            msapp.coupling = cpt

            msapp.cohesion = coht
            msapp.wsict = wsict
            msapp.numero_microservicios = contadorMS

            msapp.tiempo_estimado_desarrollo = mayor_tiempo

            msapp.avg_calls = sumacalls /  msapp.numero_microservicios
            msapp.avg_request = sumarequest /  msapp.numero_microservicios

            msapp.valor_GM = gm
            metricas= [msapp, listaMS]               

            return metricas
    
    def calcularMetricasMicroservicio(self, msCalcular, microservicios, n, dependencias):
        clientes=0 # Cuantos MS llaman a msCalcular
        request=0  # Cuantas veces llaman a msCalcular
        calls=0  # Cuantas llamadas hace msCalcular a otros MS
        provedores=0 # Cuantos MS usa o llama msCalcular
        interdependientes=0
        nointerdependientes=0
        vector_callsIJ=[]        
        puntos=0
        tiempo=0
        valor=0
        valor2=0
        numero_historias=0
        i=0
        if microservicios:            
            for ms in microservicios:                
                callsIJ=0 # Llamadas que hace el MSCal a cada MS
                valor=0
                valor2=0
                if ms[0] != msCalcular[0]:
                    # Calcular AIS - Request (Peticiones)
                    historias = ms[1]
                    historiasmscal = msCalcular[1]
                    for hu in historias:                        
                        for hums in historiasmscal:
                            #cont = Dependencia_Historia.objects.filter(historia = hu, dependencia = hums).count()
                            #cont2 = Dependencia_Historia.objects.filter(historia = hums, dependencia = hu).count()

                            #if cont>0:
                            if [hu.id, hums.id] in dependencias:
                                valor+=1
                                request+=1
                            
                            #if cont2>0:
                            if [hums.id, hu.id] in dependencias:
                                valor2+=1
                                calls+=1
                                callsIJ+=1
                            
                            if i==0:
                                tiempo+=hums.tiempo_estimado
                                puntos+=hums.puntos_estimados
                                numero_historias += 1
                                
                        i+=1
                    if valor>0:
                        clientes+=1 
                    if valor2>0:
                        provedores+=1
                    
                    if valor>0 and valor2>0:
                        interdependientes+=1
                    else:
                        nointerdependientes+=1
                vector = [callsIJ]                
                vector_callsIJ.extend(vector)    
                grado_cohesion = nointerdependientes / n
                wsic = numero_historias
    
        respuesta = [clientes, request, provedores, calls, interdependientes, nointerdependientes, grado_cohesion, wsic, tiempo, puntos, vector_callsIJ]
        return respuesta
                                        
                    



