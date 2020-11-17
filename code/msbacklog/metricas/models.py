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
    
    def calcularMetricasMS(self, msCalcular, microservicios, n, dependencias, penalizaCx):
        clientes=0 # Cuantos MS llaman a msCalcular
        request=0  # Cuantas veces llaman a msCalcular
        calls=0  # Cuantas llamadas hace msCalcular a otros MS
        provedores=0 # Cuantos MS usa o llama msCalcular
        interdependientes=0
        nointerdependientes=0
        vector_callsIJ=[]
        vector_cx=[]
        vector_cxr=[]        
        puntos=0
        tiempo=0
        valor=0
        valor2=0
        numero_historias=0
        i=0
        cx=0 # Complejidad de llamadas (calls) del microservicio a otros microservicios.
        cxr=0 # complejidad de peticiones (request) que hacen al microservicio
        historiasmscal = Microservicio_Historia.objects.filter(microservicio = msCalcular)

        if microservicios:
            for ms in microservicios:
                callsIJ=0 # Llamadas que hace el MSCal a cada MS
                requestIJ=0 # Peticiones que cada MS hace al MSCal
                valor=0
                valor2=0

                if ms.id != msCalcular.id:
                    historias = Microservicio_Historia.objects.filter(microservicio = ms)                    
                    for hu in historias:                        
                        for hums in historiasmscal:
                            #cont = Dependencia_Historia.objects.filter(historia = hu, dependencia = hums).count()
                            #cont2 = Dependencia_Historia.objects.filter(historia = hums, dependencia = hu).count()

                            #if cont>0:
                            if [hu.historia.id, hums.historia.id] in dependencias:
                                valor+=1
                                request+=1
                                requestIJ+=1
                            
                            #if cont2>0:
                            if [hums.historia.id, hu.historia.id] in dependencias:
                                valor2+=1
                                calls+=1
                                callsIJ+=1                                                        
                                
                        i+=1
                    if valor>0:
                        clientes+=1 
                    if valor2>0:
                        provedores+=1
                    
                    cx = callsIJ
                    cxr = requestIJ
                    
                    if valor>0 and valor2>0:
                        interdependientes+=1
                        cx =  cx * int(penalizaCx)
                        cxr = cxr * int(penalizaCx)
                    else:
                        nointerdependientes+=1                                

                vector = [callsIJ]                
                vector_callsIJ.extend(vector)                                    
                vector1 = [cx]
                vector_cx.extend(vector1)
                vector2 = [cxr]
                vector_cxr.extend(vector2)
            
            for hums in historiasmscal:
                tiempo+=hums.historia.tiempo_estimado
                puntos+=hums.historia.puntos_estimados
                numero_historias += 1
            
            grado_cohesion = nointerdependientes / n
            wsic = numero_historias
    
        respuesta = [clientes, request, provedores, calls, interdependientes, nointerdependientes, grado_cohesion, 
                     wsic, tiempo, puntos, vector_callsIJ, vector_cx, vector_cxr]
        return respuesta

    def calcularMetricasMSApp(self, msapp, dependencias, penalizaCx, totalHistorias, totalPuntos):
        microservicios = Microservicio.objects.filter(aplicacion = msapp)

        if microservicios:
            sumacalls = 0.0
            sumarequest = 0.0
            mayor_tiempo = 0.0

            sumacuaAIS=0
            sumacuaADS=0
            sumacuaSIY=0
            sucmacuaCoh=0
            sumaCgi=0
            sumaPuntos=0
            mayor_wsic=0
            mayor_puntos=0
            n= len(microservicios)
            contadorMS=0
            vector_cgs=[] # Peso de los nodos o microservicios
            vector_cxs=[] # Calls (out) de MS a otros con penalización si es bidireccional
            vector_cxrs=[] #  Calls (in) de otros a MS con penalización si es bidireccional
            vector_callsij=[] # número de calls entre MS
            suma_siy=0

            for ms in microservicios:
                contadorMS += 1
                # calcular las métricas del microservicio
                rta = self.calcularMetricasMS(ms, microservicios, n, dependencias, penalizaCx)

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

                #cgi = ms.total_puntos * ms.numero_historias # Peso de cada nodo del grafo de microservicios
                #cgi = ms.total_puntos / ms.numero_historias # Peso de cada nodo del grafo de microservicios
                #cgi = ms.total_puntos + ms.numero_historias
                #cgi = float(ms.total_puntos + ms.numero_historias) / float(totalHistorias + totalPuntos)
                cgi = ms.total_puntos
                ms.complejidad_cognitiva = ms.total_puntos

                vector=[cgi] 
                vector_cgs.extend(vector) # Guardo los pesos de cada nodo de la aplicación.
                vector2 = [ms,rta[10]]
                vector_callsij.append(vector2)
                vector_cxs.append(rta[11]) # Obtengo el valor de llamadas entre el microservicio y los otros aplicando la penalización si son bidireccionales.
                vector_cxrs.append(rta[12])

                if ms.tiempo_estimado_desarrollo > mayor_tiempo:
                    mayor_tiempo = ms.tiempo_estimado_desarrollo

                sumaCgi += (ms.total_puntos * ms.calls) + (ms.total_puntos * ms.request )
                sumaPuntos += ms.total_puntos
                sumacalls += ms.calls
                sumarequest += ms.request

                sumacuaAIS += ms.ais * ms.ais
                sumacuaADS += ms.ads * ms.ads
                sumacuaSIY += ms.siy * ms.siy

                sucmacuaCoh += ms.grado_cohesion * ms.grado_cohesion
                suma_siy += ms.siy

                if ms.numero_historias > mayor_wsic:
                    mayor_wsic = ms.numero_historias
                
                if ms.total_puntos > mayor_puntos:
                    mayor_puntos = ms.total_puntos
                
                ms.save()
                
            # Calcular la complejidad cognitiva
            cgt=0  # Cgt guarda el valor de la profundidad multiplicada por el peso de cada nodo por donde pasa hasta encontrar un ciclo.
            i=0           
            for i in range (0, n):                
                p=0
                calls=0
                fila = vector_callsij[i]
                ms1 = fila[0]
                #cgt += ms.complejidad_cognitiva
                memo = []
                p = self.calcularProfundidad(vector_callsij, n, i, memo, p, cgt, calls)
                #cgt += vector[0] * vector[1]   
                if p==0:
                    prof=0
                else:
                    prof = len(memo)       
                #cgi=0                      
                # for ind in memo:
                #     ms = vector_callsij[ind][0]
                #     cgi += ms.complejidad_cognitiva 
                
                cgt += prof
                #print("--------------- Memo: " + memo)
            
            # Complejidad del mayor numero de historias asociadas a un microservicio y el numero de microservicios
            cgh = n * mayor_wsic 

            # if sumacalls>0:
            #     valor1= float(sumaCgi)  / float(sumacalls)
            # else:
            #     valor1=0
            valor1= sumaCgi

            # Complejidad cognitiva total - Dificultad de entender, mantener e implenetar la solución planteada.
            # suma_siy --> suma del número de microservicios que son interdependientes
            cxt = ( valor1 + mayor_puntos ) + cgh + cgt + suma_siy
 
            # Calcular complejidad cognitiva en relación a la complejidad mas baja: 1 microservicios con 1 historia de usuario y 1 punto de historia
            # Pare el caso de menor complejidad la complejidad cognitiva sería 2
            msapp.complejidad_cognitiva = cxt / 2

            #cxt= valor1/0

            # Calls (out)
            # sumaCx=0 
            # i=0
            # for cx in vector_cxs:
            #     sumaCxi=0
            #     j=0         
            #     cgmsi =  vector_cgs[i]       
            #     for call in cx:                    
            #         cgmsj = vector_cgs[j]                    
            #         valor_cx = call #* cgmsj                    
            #         sumaCxi = sumaCxi +  valor_cx
            #         j+=1
            #     sumaCx += sumaCxi + cgmsi
            #     i+=1
            
            # Request (in)
            # sumaCxr=0
            # i=0
            # for cxr in vector_cxrs:
            #     sumaCxri=0
            #     cgmsi = vector_cgs[i]
            #     for reques in cxr:                                        
            #         valor_cxr = reques #* cgmsi
            #         sumaCxri = sumaCxri + valor_cxr
            #     sumaCxr+= sumaCxri
            #     i+=1

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

            wsict = mayor_wsic
            #cplt = sumaCx + sumaCxr
            #semant = 0
            
            # if variables:
            #     for var in variables:
            #         if var=="coupling":                    
            #             cua_copt = cpt * cpt 
            #         if var=="cohesion":
            #             cua_coht = coht * coht
            #         if var=="complexity":
            #             cua_cplt = cplt * cplt 
            #         if var=="wsict":
            #             cua_wsict = wsict * wsict
            #         if var=="semantic":
            #             cua_semant = semant * semant # Falta crear el método de calcular la similitud semantica de la MSApp

            #gm = math.sqrt( (cua_coht) + (cua_copt) + (cua_wsict) + (cua_cplt) + (cua_semant) )
            
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

            #msapp.complejidad_cognitiva = sumaCx + sumaCxr +  msapp.numero_microservicios
            #msapp.complejidad_cognitiva = cgt
            msapp.valor_GM = self.calcularMetricaGranularidadGM(msapp.cohesion, msapp.coupling, msapp.wsict)
            msapp.save()

    def calcularProfundidad(self, matrizCalls, n, index, memo, p, cgt, calls):
        fila = matrizCalls[index]
        ms = fila[0]
        callsij = fila[1]
        #cgt += ms.complejidad_cognitiva * calls        
        if not index in memo:
            #cgt += ms.complejidad_cognitiva
            #p+=1            
        #else:            
            if ms.calls > 0:
                for j in range(0, n):
                    vec = [index]         
                    if not index in memo:
                        memo.extend(vec)
                    if callsij[j] > 0:
                        p+=1                                  
                        p = self.calcularProfundidad(matrizCalls, n, j, memo, p, cgt, callsij[j])
                        #p= vec[0]
                        #cgt = vec[1]
            else:
                vec = [index]         
                if not index in memo:
                    memo.extend(vec)
        
        #vector= [p,cgt]
        #return vector
        return p

            
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

    # Método usado para calcular las metricas del individuo usado por el algoritmo genético
    def calcularMetricasIndividuo(self, microservicios, variables, dependencias, penalizaCx, totalHistorias, totalPuntos, similitud):        
        if microservicios:
            sumacalls = 0.0
            sumarequest = 0.0
            mayor_tiempo=0

            listaMS=[]
            sumacuaAIS=0
            sumacuaADS=0
            sumacuaSIY=0
            sucmacuaCoh=0
            suma_siy=0
            sumaCgi=0
            sumaPuntos=0
            mayor_wsic=0
            mayor_puntos=0
            n= len(microservicios)
            contadorMS=0
            vector_cgs=[] # Peso de los nodos o microservicios
            vector_cxs=[] # Calls (out) de MS a otros
            vector_cxrs=[] #  Calls (in) de otros a MS
            vector_callsij=[] # numero de calls entre MS
            suma_similitud =0           

            for dato in microservicios:                
                contadorMS += 1
                nombreMS = dato[0]

                ms = Microservicio(nombre= nombreMS)

                # calcular las métricas del microservicio
                rta = self.calcularMetricasMicroservicio(dato, microservicios, n, dependencias, penalizaCx, similitud)

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

                #cgi = ms.total_puntos * ms.numero_historias # Peso de cada nodo del grafo de microservicios
                #cgi = ms.total_puntos / ms.numero_historias # Peso de cada nodo del grafo de microservicios
                #cgi = ms.total_puntos + ms.numero_historias
                #cgi = float(ms.total_puntos + ms.numero_historias) / float(totalHistorias + totalPuntos)
                cgi = ms.total_puntos
                ms.complejidad_cognitiva = ms.total_puntos

                vector=[cgi] 
                vector_cgs.extend(vector) # Guardo los pesos de cada nodo de la aplicación.
                vector2= [ms, rta[10]]
                vector_callsij.append(vector2)
                vector_cxs.append(rta[11]) # Obtengo el valor de llamadas entre el microservicio y los otros aplicando la penalización si son bidireccionales.
                vector_cxrs.append(rta[12])

                ms.similitud_semantica = rta[13]

                if ms.tiempo_estimado_desarrollo > mayor_tiempo:
                    mayor_tiempo = ms.tiempo_estimado_desarrollo

                sumaCgi += (ms.total_puntos * ms.calls) + (ms.total_puntos * ms.request)
                sumaPuntos += ms.total_puntos
                sumacalls += ms.calls
                sumarequest += ms.request

                sumacuaAIS += ms.ais * ms.ais
                sumacuaADS += ms.ads * ms.ads
                sumacuaSIY += ms.siy * ms.siy

                sucmacuaCoh += ms.grado_cohesion * ms.grado_cohesion
                suma_siy += ms.siy
                suma_similitud += ms.similitud_semantica

                if ms.numero_historias > mayor_wsic:
                    mayor_wsic = ms.numero_historias
                
                if ms.total_puntos > mayor_puntos:
                    mayor_puntos = ms.total_puntos

                vector= [ms, dato[1]]
                listaMS.append(vector)            

            # Calcular la complejidad cognitiva            
            cgt=0
            i=0

            for i in range (0, n):                
                p=0
                calls=0
                fila = vector_callsij[i]
                ms1 = fila[0]
                #cgt += ms.complejidad_cognitiva
                memo = []
                p = self.calcularProfundidad(vector_callsij, n, i, memo, p, cgt, calls)
                #cgt += vector[0] * vector[1]   
                if p==0:
                    prof=0
                else:
                    prof = len(memo)       
                cgi=0                      
                # for ind in memo:
                #     ms = vector_callsij[ind][0]
                #     cgi += ms.complejidad_cognitiva 
                
                cgt += prof
                #print("--------------- Memo: " + memo)
            
            # Complejidad del mayor numero de historias asociadas a un microservicio y el numero de microservicios
            cgh = contadorMS * mayor_wsic 

            #if sumacalls>0:
            #    valor1= float(sumaCgi)  / float(sumacalls)
            #else:
            #    valor1=0

            # Complejidad cognitiva total - Dificultad de entender, mantener e implenetar la solución planteada.
            valor1= sumaCgi
            cxt = ( valor1 + mayor_puntos ) + cgh + cgt + suma_siy                        

            cua_coht=0
            cua_copt=0
            cua_wsict=0
            cua_cplt=0
            cua_semant=0

            aist = math.sqrt(sumacuaAIS)
            adst = math.sqrt(sumacuaADS)
            siyt = math.sqrt(sumacuaSIY)
            cpt = math.sqrt( (aist*aist) + (adst*adst) + (siyt*siyt))
            cpt = cpt * 10

            coht = math.sqrt(sucmacuaCoh)

            wsict = mayor_wsic
            cplt = cxt / 2            
            semant = (suma_similitud / n)*100
            
            if variables:
                for var in variables:
                    if var=="coupling":                    
                        cua_copt = cpt * cpt 
                    if var=="cohesion":
                        cua_coht = coht * coht
                    if var=="complexity":
                        cua_cplt = cplt * cplt 
                    if var=="wsict":
                        cua_wsict = wsict * wsict
                    if var=="semantic":
                        cua_semant = (100-semant)*(100-semant) 

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
            msapp.similitud_semantica = semant

            # Calcular complejidad cognitiva en relación a la complejidad mas baja: 1 microservicios con 1 historia de usuario y 1 punto de historia
            # Pare el caso de menor complejidad la complejidad cognitiva sería 2
            msapp.complejidad_cognitiva = cxt / 2
            #msapp.complejidad_cognitiva = sumaCx + sumaCxr + msapp.numero_microservicios
            
            msapp.valor_GM = gm
            metricas= [msapp, listaMS]               

            return metricas
    
    def calcularMetricasMicroservicio(self, msCalcular, microservicios, n, dependencias, penalizaCx, similitud):
        clientes=0 # Cuantos MS llaman a msCalcular
        request=0  # Cuantas veces llaman a msCalcular
        calls=0  # Cuantas llamadas hace msCalcular a otros MS
        provedores=0 # Cuantos MS usa o llama msCalcular
        interdependientes=0
        nointerdependientes=0
        vector_callsIJ=[]
        vector_cx=[]
        vector_cxr=[]        
        puntos=0
        tiempo=0
        valor=0
        valor2=0
        numero_historias=0
        i=0
        cx=0 # Complejidad de llamadas (calls) del microservicio a otros microservicios.
        cxr=0 # complejidad de peticiones (request) que hacen al microservicio
        if microservicios:            
            for ms in microservicios:                
                callsIJ=0 # Llamadas que hace el MSCal a cada MS
                requestIJ=0 # Peticiones que cada MS hace al MSCal
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
                                requestIJ+=1
                            
                            #if cont2>0:
                            if [hums.id, hu.id] in dependencias:
                                valor2+=1
                                calls+=1
                                callsIJ+=1                                                                                        
                        i+=1
                    if valor>0:
                        clientes+=1 
                    if valor2>0:
                        provedores+=1
                    
                    cx = callsIJ
                    cxr = requestIJ
                    
                    if valor>0 and valor2>0:
                        interdependientes+=1
                        cx =  cx * int(penalizaCx)
                        cxr = cxr * int(penalizaCx) 
                    else:
                        nointerdependientes+=1
                vector = [callsIJ]                
                vector_callsIJ.extend(vector)                                    
                vector1 = [cx]
                vector_cx.extend(vector1)
                vector2 = [cxr]
                vector_cxr.extend(vector2)

            historiasmscal = msCalcular[1]

            for hums in historiasmscal:
                tiempo+=hums.tiempo_estimado
                puntos+=hums.puntos_estimados
                numero_historias += 1
            
            suma_similitud=0
            similitudMs=0
            cont=0

            # Calcular la similitud semantica del microservicio
            for k in range(0, (numero_historias - 1)):
                for l in range ((k+1), numero_historias):
                    hu1 = historiasmscal[k]
                    hu2 = historiasmscal[l]
                    key = hu1.identificador + "-" + hu2.identificador
                    valor = similitud.get(key)            
                    if valor==None:
                        key = hu2.identificador + "-" + hu1.identificador
                        valor = similitud.get(key)
                        if valor== None:
                            valor=0
                        else:
                            suma_similitud += valor
                            cont+=1    
                    else:        
                        suma_similitud += valor
                        cont+=1
            if cont==0:
                cont=1
            similitudMs = suma_similitud / cont

            grado_cohesion = nointerdependientes / n
            wsic = numero_historias
    
        respuesta = [clientes, request, provedores, calls, interdependientes, nointerdependientes, grado_cohesion, 
                     wsic, tiempo, puntos, vector_callsIJ, vector_cx, vector_cxr, similitudMs]
        return respuesta
                                        
                    



