# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import spacy
from microservicios.models import Microservicio, Microservicio_Historia
from historiasUsuario.models import HistoriaUsuario, Dependencia_Historia
from metricas.models import Metrica
from random import randint
import math
import copy
from time import time
from multiprocessing import Pool, cpu_count
from collections import Counter

# Create your models here.
class Clustering():
    nlp=None
    def __init__(self, lenguaje, modulo):
        if lenguaje == 'es':
            if modulo == 'md':
                self.nlp = spacy.load("es_core_news_md")
            if modulo == 'sm':
                self.nlp = spacy.load("es_core_news_sm")
        if lenguaje == 'en':
            if modulo == 'md':
                self.nlp = spacy.load("en_core_web_md")
            if modulo == 'sm':
                self.nlp = spacy.load("en_core_web_sm")
            
    
    def identificarVerbosEntidades(self, historiaUsuario):
        texto = historiaUsuario.nombre + ": " + historiaUsuario.descripcion
        #texto = historiaUsuario.nombre
        doc = self.nlp(texto)
        listaText=''
        listLemmas=''        
        lista=[]
        for token in doc:
            pos = token.pos_
            if pos == 'NOUN' or pos == 'PROPN':                                  
                hutoken = [token.text, token.lemma_, token.pos_, token.vector_norm, token.has_vector]
                listaText += token.text + ' '
                listLemmas += token.lemma_ + ' '
        lista = [historiaUsuario, listaText, listLemmas]
        return lista
    
    def identificarEntidadHistorias(self, listaHistorias):
        listaEntidadesHU=[]
        for historia in listaHistorias:
            lista = self.identificarVerbosEntidades(historia)
            textos= lista[1]
            lemmas = lista[2]            
            frecuenciaText = Counter(textos.split(' '))        
            frecuencaLema = Counter(lemmas.split(' '))
            
            dicText = frecuenciaText.most_common(2)
            dicLema = frecuencaLema.most_common(2)

            entidadText=""
            for txt in dicText:
                entidadText += str(txt[0]) + " "
            
            entidadLema=""
            for txt in dicLema:
                entidadLema += str(txt[0]) + " "            

            vector = [historia, entidadText, entidadLema]            
            listaEntidadesHU.append(vector)        
        return listaEntidadesHU
    
    def agruparPorFrecuenciaEntidad(self, listaFrecuencias, pAgrupar, aplicarEn):
        listaMs=[]
        index=0        
        contador=0
        similar = False        
                
        for dato in listaFrecuencias:    
            index=0        
            similar= False
            for ms in listaMs: 
                similitud=0.0               
                #avg_simlitud=0
                #dictTextoDato = dato[1]
                #dictTextoMS = ms[1]                      

                #dicMS = dictTextoMS[0]     

                #textoMS = ms[0][0].nombre + " " + ms[0][0].descripcion                
                #textoDato = dato[0].nombre + " " + dato[0].descripcion                               

                pAgrupar = round(pAgrupar, 3) 

                if aplicarEn == 'text':
                    textoMS = ms[0][1]
                    textoDato = dato[1]
                    doc1 = self.nlp(textoMS)
                    doc2 = self.nlp(textoDato)
                    similitud = doc1.similarity(doc2)
                    similitud = round(similitud, 3)

                if aplicarEn == 'lemma':
                    lemmaMS = ms[0][2]
                    lemmaDato = dato[2]
                    doc1 = self.nlp(lemmaMS)
                    doc2 = self.nlp(lemmaDato)
                    similitud = doc1.similarity(doc2)
                    similitud = round(similitud, 3)                                

                if similitud >= pAgrupar:
                    vector =  listaMs[index]
                    vector2 = dato
                    vector.append(vector2)
                    listaMs[index] = vector
                    similar=True
                    break

                index += 1
            
            if similar==False:
                vector= [dato]                
                listaMs.append(vector)
                contador += 1

        return listaMs
    
    def reAgruparMicroservicios(self, msapp, dependencias, pAgrupar, pSemantica, aplicarEn):
        matrizCalls = self.calcularDistanciaCalls(msapp, dependencias)
        listMs = Microservicio.objects.filter(aplicacion = msapp)

        n=len(listMs)
        i=0
        mem_agrupados=[]
        microservicios=[]
        total_calls = msapp.getTotalCalls()
        for ms in listMs:
                        
            dato = matrizCalls[i]
            unircon = []
            for j in range(i+1,n):
                vector= dato[j]
                msCompara = vector[0]
                call = vector[1]
                reques = vector[2]

                # Agrupar interdependientes
                # Agrupar por entidades - Microservicios que se refieran a lo mismo
                list1 = self.identificarEntidadesMicroservicio(ms)
                list2 = self.identificarEntidadesMicroservicio(msCompara)

                if aplicarEn == 'text':
                    textoMS = list1[3]
                    textoDato = list2[3]
                    doc1 = self.nlp(textoMS)
                    doc2 = self.nlp(textoDato)
                    similitud = doc1.similarity(doc2)
                    similitud = round(similitud, 3)

                if aplicarEn == 'lemma':
                    lemmaMS = list1[4]
                    lemmaDato = list2[4]
                    doc1 = self.nlp(lemmaMS)
                    doc2 = self.nlp(lemmaDato)
                    similitud = doc1.similarity(doc2)
                    similitud = round(similitud, 3)                                

                if similitud >= pSemantica:
                    msnew = [msCompara]
                    unircon.extend(msnew)
                else:
                    if call>0 and reques>0:
                        msnew = [msCompara]
                        unircon.extend(msnew)                    
                    else:
                        # Agrupar por distancia de agrupamiento
                        distancia = float(call + reques) / float(total_calls)
                        if (distancia>pAgrupar):
                            msnew = [msCompara]
                            unircon.extend(msnew)
                        else:                                                        
                            # Agrupar por punto critico
                            #distancia = float(msCompara.request) / float(total_calls)

                            #if distancia>pAgrupar:           

            vector2= [ms, unircon]
            microservicios.append(vector2)
            i+=1


        return msapp
    
    def identificarEntidadesMicroservicio(self, ms):
        historias = ms.getHistorias()
        texto=""
        for hu in historias:
            texto += hu.nombre + " " + hu.descripcion
        
        doc = self.nlp(texto)
        for token in doc:
            pos = token.pos_
            if pos == 'NOUN' or pos == 'PROPN':                                                  
                listaText += token.text + ' '
                listLemmas += token.lemma_ + ' '
        
        frecuenciaText = Counter(listaText.split(' '))        
        frecuencaLema = Counter(listLemmas.split(' '))
            
        dicText = frecuenciaText.most_common(3)
        dicLema = frecuencaLema.most_common(3)

        entidadText=""
        for txt in dicText:
            entidadText += str(txt[0]) + " "
        
        entidadLema=""
        for txt in dicLema:
            entidadLema += str(txt[0]) + " "            
            
        lista = [ms, listaText, listLemmas, entidadText, entidadLema]
        return lista
      
    def unirMicroservicios(self, ms1, ms2):
        ms = Microservicio(
            nombre = ms1.nombre + "-" + ms2.nombre,
            numero_historias = ms1.numero_historias + ms2.numero_historias,
            similitud_semantica = ((ms1.similitud_semantica + ms2.similitud_semantica)/2),
            aplicacion = ms1.msapp
        )

        historias1 = ms1.getHistorias()
        historias2 = ms2.getHistorias() 

        historias1.extend(historias2)
        vector=[ms, historias1]
        
        return vector

                        
    def calcularSimilitud(self, listaHistorias, aplicarEn ):
        matrizSimilitud=[]
        textos=[]
        for historia in listaHistorias:
            lista = self.identificarVerbosEntidades(historia)
            textos.append(lista)
        
        for texto in textos:
            hu = texto[0]            
            tex = texto[1]
            lem = texto[2]
            if aplicarEn == 'lemma':
                doc1 = self.nlp(lem)                
            if aplicarEn == 'text':
                doc1 = self.nlp(tex)            
            similitudes=[hu]

            for tex_hu in textos:                
                hu2 = tex_hu[0]
                texto2 = tex_hu[1]
                lemma2 = tex_hu[2]
                if aplicarEn == 'lemma':
                    doc2 = self.nlp(lemma2)
                if aplicarEn == 'text':
                    doc2 = self.nlp(texto2)
                similitud = doc1.similarity(doc2)                
                dicc = [hu2, similitud]
                similitudes.append(dicc)
            
            matrizSimilitud.append(similitudes)
        return matrizSimilitud 
    
    def calcularSimilitudPar(self, index):
        #dicSimilitud={}                      
        #n = len(self.listaHistorias)
        print("---- Inicio proceso: " + index)

        i= index * index
        print("---- Index: " + index)
        
        # for j in range ((i+1), n):                                
        #     historia = self.listaHistorias[i]
        #     historia2 = self.listaHistorias[j]

        #     texto1 = self.identificarVerbosEntidades(historia)
        #     texto2 = self.identificarVerbosEntidades(historia2)
                        
        #     tex = texto1[1]
        #     lem = texto1[2]

        #     tex2 = texto2[1]
        #     lem2 = texto2[2]

        #     #tex = historia.nombre + ":" + historia.descripcion
        #     #tex2 = historia2.nombre + ":" + historia2.descripcion

        #     if self.aplicarEn == 'lemma':
        #         doc1 = self.nlp(lem)                
        #         doc2 = self.nlp(lem2)
        #     if self.aplicarEn == 'text':
        #         doc1 = self.nlp(tex)
        #         doc2 = self.nlp(tex2)    
            
        #     similitud = doc1.similarity(doc2)
        #similitud = index
        #key = historia.identificador + "-" + historia2.identificador
        #key= self.listaHistorias[i].identificador + " - " + self.listaHistorias[i+1].identificador
        #dicSimilitud[key] = similitud              
        #return dicSimilitud
        return i
    
    def calcularDiccionarioSimilitud(self, listaHistorias, aplicarEn ):
        dicSimilitud={}              
        n = len(listaHistorias)

        for i in range(0, n-1):
            for j in range ((i+1), n):                                
                historia = listaHistorias[i]
                historia2 = listaHistorias[j]

                texto1 = self.identificarVerbosEntidades(historia)
                texto2 = self.identificarVerbosEntidades(historia2)
                            
                tex = texto1[1]
                lem = texto1[2]

                tex2 = texto2[1]
                lem2 = texto2[2]

                #tex = historia.nombre + ":" + historia.descripcion
                #tex2 = historia2.nombre + ":" + historia2.descripcion

                if aplicarEn == 'lemma':
                    doc1 = self.nlp(lem)                
                    doc2 = self.nlp(lem2)
                if aplicarEn == 'text':
                    doc1 = self.nlp(tex)
                    doc2 = self.nlp(tex2)    
                
                similitud = doc1.similarity(doc2)
                key = historia.identificador + "-" + historia2.identificador
                dicSimilitud[key] = similitud              

        # Programación en paralelo - No funcionó
        # self.listaHistorias = listaHistorias
        # self.aplicarEn = aplicarEn
        # cpus = cpu_count()     
        # print("----- CPUs: " + str(cpus) )               
        # print("----- n: " + str(n) )               
        # with Pool(cpus) as pr:            
        #     print("---- Entro: ")
        #     vector = pr.map(self.calcularSimilitudPar, range(0, n))
        #     print("---- Sale: ")            
        #     pr.close
        #     pr.join            
        #     dicSimilitud = diccionario
        # print("---- Diccionario: " + str(diccionario))
        return dicSimilitud
    
    def agruparHistorias(self, mastrizSimilitud, n, pAgrupar):
        lista=[]                
        idUsados=[]
        usados=[]
        for i in range(0, n):
            listaHU = mastrizSimilitud[i]
            historia = listaHU[i+1]            
            ms = []
            cont=0
            for j in range (i+2, n):                
                dato = mastrizSimilitud[i][j]
                similitud = dato[1]
                if similitud > pAgrupar:
                    huAdd = dato[0]
                    if huAdd.id in idUsados:
                        index = idUsados.index(huAdd.id)
                        valorComp = usados[index]   # [hu, i, j, similitud]
                        simiCom = valorComp[3]
                        if similitud > simiCom: 
                            # Se reemplaza el valor y se elimina del MS
                            #lista[valorComp[1]].pop(valorComp[2])  # Quitarlo de la Lista anterior
                            valElim = [valorComp[0],valorComp[3]]
                            lista[valorComp[1]].remove(valElim)
                            usados.pop(index) # quitar de usados
                            idUsados.pop(index)
                            # Agregar el nuevo valor
                            vector = [huAdd, similitud]            
                            ms.append(vector)                                                                                
                            vectorId= [huAdd.id]
                            idUsados.extend(vectorId)
                            datoUsa = [huAdd, i, cont, similitud]
                            usados.append(datoUsa)                        
                            cont += 1
                    else:
                        vectorId= [huAdd.id]    
                        idUsados.extend(vectorId)
                        datoUsa = [huAdd, i, cont, similitud]
                        usados.append(datoUsa)
                        vector = [huAdd, similitud]                    
                        ms.append(vector)
                        cont += 1
            #if cont>1:
            lista.append(ms)        
        idUsados=[]
        usados=[]
        i=0
        cont=0
        microservicios=[]        
        for lt in lista: 
            ms=[]                                   
            numeroHU = len(lt)
            if numeroHU>0 :
                # Agregar la historia de usuario padre 
                dato = mastrizSimilitud[i][i+1]
                huini = dato[0]
                similitud = dato[1]
                if huini.id in idUsados:
                    index = idUsados.index(huini.id)
                    valorComp = usados[index]   # [hu, similitud]
                    simiCom = valorComp[2]
                    if similitud > simiCom: 
                        # Se reemplaza el valor y se elimina del MS
                        #lista[valorComp[1]].pop(valorComp[2])  # Quitarlo de la Lista anterior
                        valElim = [valorComp[0], valorComp[2]]
                        microservicios[valorComp[1]].remove(valElim)
                        # quitar de usados
                        usados.pop(index) 
                        idUsados.pop(index)
                        # Agregar el nuevo valor
                        vector = [huini, similitud]            
                        ms.append(vector)                                                                                
                        vectorId= [huini.id]
                        idUsados.extend(vectorId)
                        datoUsa = [huini, cont, similitud]
                        usados.append(datoUsa)                                                        
                else:
                    vector = [huini, similitud]            
                    ms.append(vector)                                                                                
                    vectorId= [huini.id]
                    idUsados.extend(vectorId)
                    datoUsa = [huini, cont, similitud]
                    usados.append(datoUsa)
                # Agregar las historias de con similitud semantica a huini
                for j in range (0, numeroHU):                 
                    huadd = lt[j]
                    hu = huadd[0]
                    similitud = huadd[1]
                    if hu.id in idUsados:
                        index = idUsados.index(hu.id)
                        valorComp = usados[index]   # [hu, similitud]
                        simiCom = valorComp[2]
                        if similitud > simiCom: 
                            # Se reemplaza el valor y se elimina del MS
                            #lista[valorComp[1]].pop(valorComp[2])  # Quitarlo de la Lista anterior
                            valElim = [valorComp[0], valorComp[2]]
                            microservicios[valorComp[1]].remove(valElim)
                            # quitar de usados
                            usados.pop(index) 
                            idUsados.pop(index)
                            # Agregar el nuevo valor
                            vector = [hu, similitud]            
                            ms.append(vector)                                                                                
                            vectorId= [hu.id]
                            idUsados.extend(vectorId)
                            datoUsa = [hu, cont,similitud]
                            usados.append(datoUsa)
                       # comparar la similitud y dejar el de  mayor similaridad
                    else:
                         # Agregar HU al microservicios
                        vectorId = [huadd[0].id]
                        idUsados.extend(vectorId)
                        datoUsa = [huadd[0], cont, huadd[1] ]
                        usados.append(datoUsa)
                        vector = [huadd[0], huadd[1]]
                        ms.append(vector)
            else:
                # Agregar la historia de usuario cuando no tuvo similitud con ninguna otra
                dato = mastrizSimilitud[i][i+1]
                huini = dato[0]
                similitud = dato[1]
                if huini.id not in idUsados:
                    vector = [huini, similitud]            
                    ms.append(vector)                                                                                
                    vectorId= [huini.id]
                    idUsados.extend(vectorId)
                    datoUsa = [huini, cont, similitud]
                    usados.append(datoUsa)                    
            if len(ms) > 0:
                microservicios.append(ms)
                cont += 1
            i += 1
        return microservicios    
    
    def calcularDistanciaCalls(self, msapp, dependencias):        
        matrizCalls=[]
        listMS = Microservicio.objects.filter(aplicacion= msapp)
        vector=[]        
        if listMS:
            for ms in listMS:
                call=0 
                request=0      
                vector = []         
                for ms2 in listMS:
                    if ms.id == ms2.id:
                        call=0
                        request=0
                        #dato = [ms, call]
                        #vector.append(dato)
                    else:
                        historias = Microservicio_Historia.objects.filter(microservicio = ms)
                        historiasmscal = Microservicio_Historia.objects.filter(microservicio = ms2)
                        valor=0
                        valor2=0
                        for hu in historias:                        
                            for hums in historiasmscal:
                                cont = Dependencia_Historia.objects.filter(historia = hu.historia, dependencia = hums.historia).count()                                
                                cont2 = Dependencia_Historia.objects.filter(historia = hums.historia, dependencia = hu.historia).count()
                                #if  [hu.id, hums.id] in dependencias:
                                if cont>0:
                                    valor+=1
                                if cont2>0:
                                    valor2+=1
                        call = valor
                        request = valor2
                    dato = [ms2, call, request]                                        
                    vector.append(dato)
                matrizCalls.append(vector)                      
        return matrizCalls
    
    def calcularDistanciaCoupling(self, msapp):
        
        # Calcular las métricas
        metrica = Metrica()
        metrica.calcularMetricas(msapp)
        
        listaMs = Microservicio.objects.filter(aplicacion = msapp)
        matrizDistancia=[]
        for msi in listaMs:
            vector=[]
            for msj in listaMs:
                
                if not msi.id==msj.id:
                    distancia = math.sqrt ( math.pow( (msj.ais - msi.ais), 2) + math.pow((msj.ads - msi.ads),2 ) + math.pow((msj.siy - msi.siy ),2))
                else:
                    distancia=0
                nivel = distancia / msapp.coupling
                dato = [msj, nivel]
                vector.append(dato)
            vector2 = [msi, vector]
            matrizDistancia.append(vector2)
    
        return matrizDistancia

    def agruparMicroservicios(self, matrizDistancia, n, pAgrupar):
        lista=[]                
        idUsados=[]
        usados=[]
        for i in range(0, n):
            listaMS = matrizDistancia[i]
            ms = listaMS[0]            
            microservicio = []
            cont=0
            for j in range (i+1, n):                
                dato = listaMS[1][j]
                similitud = dato[1]
                if similitud > pAgrupar:
                    msAdd = dato[0]
                    if msAdd.id in idUsados:
                        index = idUsados.index(msAdd.id)
                        valorComp = usados[index]   # [ms, i, j, similitud]
                        simiCom = valorComp[3]
                        if similitud > simiCom: 
                            # Se reemplaza el valor y se elimina del MS
                            #lista[valorComp[1]].pop(valorComp[2])  # Quitarlo de la Lista anterior
                            valElim = [valorComp[0],valorComp[3]]
                            lista[valorComp[1]].remove(valElim)
                            usados.pop(index) # quitar de usados
                            idUsados.pop(index)
                            # Agregar el nuevo valor
                            vector = [msAdd, similitud]            
                            microservicio.append(vector)                                                                                
                            vectorId= [msAdd.id]
                            idUsados.extend(vectorId)
                            datoUsa = [msAdd, i, cont, similitud]
                            usados.append(datoUsa)                        
                            cont += 1
                    else:
                        vectorId= [msAdd.id]    
                        idUsados.extend(vectorId)
                        datoUsa = [msAdd, i, cont, similitud]
                        usados.append(datoUsa)
                        vector = [msAdd, similitud]                    
                        microservicio.append(vector)
                        cont += 1
            #if cont>1:
            lista.append(microservicio)        
        idUsados=[]
        usados=[]
        i=0
        cont=0
        microservicios=[]        
        for lt in lista: 
            microservicio=[]                                   
            numeroMS = len(lt)
            if numeroMS>0 :
                # Agregar microservicio padre 
                dato = matrizDistancia[i]
                msini = dato[0]
                datoDis = dato[1][i]
                similitud =  datoDis[1]
                if msini.id in idUsados:
                    index = idUsados.index(msini.id)
                    valorComp = usados[index]   # [ms, similitud]
                    simiCom = valorComp[2]
                    if similitud > simiCom: 
                        # Se reemplaza el valor y se elimina del MS
                        #lista[valorComp[1]].pop(valorComp[2])  # Quitarlo de la Lista anterior
                        valElim = [valorComp[0], valorComp[2]]
                        microservicios[valorComp[1]].remove(valElim)
                        # quitar de usados
                        usados.pop(index) 
                        idUsados.pop(index)
                        # Agregar el nuevo valor
                        vector = [msini, similitud]            
                        microservicio.append(vector)                                                                                
                        vectorId= [msini.id]
                        idUsados.extend(vectorId)
                        datoUsa = [msini, cont, similitud]
                        usados.append(datoUsa)                                                        
                else:
                    vector = [msini, similitud]            
                    microservicio.append(vector)                                                                                
                    vectorId= [msini.id]
                    idUsados.extend(vectorId)
                    datoUsa = [msini, cont, similitud]
                    usados.append(datoUsa)
                # Agregar las historias de con similitud a msini
                for j in range (0, numeroMS):                 
                    msadd = lt[j]
                    ms = msadd[0]
                    similitud = msadd[1]
                    if ms.id in idUsados:
                        index = idUsados.index(ms.id)
                        valorComp = usados[index]   # [hu, similitud]
                        simiCom = valorComp[2]
                        if similitud > simiCom: 
                            # Se reemplaza el valor y se elimina del MS
                            #lista[valorComp[1]].pop(valorComp[2])  # Quitarlo de la Lista anterior
                            valElim = [valorComp[0], valorComp[2]]
                            microservicios[valorComp[1]].remove(valElim)
                            # quitar de usados
                            usados.pop(index) 
                            idUsados.pop(index)
                            # Agregar el nuevo valor
                            vector = [ms, similitud]            
                            microservicio.append(vector)                                                                                
                            vectorId= [ms.id]
                            idUsados.extend(vectorId)
                            datoUsa = [ms, cont,similitud]
                            usados.append(datoUsa)
                       # comparar la similitud y dejar el de  mayor similaridad
                    else:
                         # Agregar ms al microservicios
                        vectorId = [msadd[0].id]
                        idUsados.extend(vectorId)
                        datoUsa = [msadd[0], cont, msadd[1] ]
                        usados.append(datoUsa)
                        vector = [msadd[0], msadd[1]]
                        microservicio.append(vector)
            else:
                # Agregar el microservicio cuando no tuvo similitud con ninguna otra
                datoms = matrizDistancia[i] 
                dato = datoms[1][i]
                msini = dato[0]
                similitud = dato[1]
                if msini.id not in idUsados:
                    vector = [msini, similitud]            
                    microservicio.append(vector)                                                                                
                    vectorId= [msini.id]
                    idUsados.extend(vectorId)
                    datoUsa = [msini, cont, similitud]
                    usados.append(datoUsa)                    
            if len(microservicio) > 0:
                microservicios.append(microservicio)
                cont += 1
            i += 1
        return microservicios

    def generarGrupoMS(self, matrizMicroservicios):        
        matrizMSHU=[]
        i=1
        for dato in matrizMicroservicios:
            nombre = "MS" + str(i)
            lista=[] # Lista de historias a guardar en el nuevo MS
            for grupo  in dato:
                ms = grupo[0] # ms antiguo microservicio
                listHU = Microservicio_Historia.objects.filter(microservicio=ms)
                for hums in listHU:
                    vector= [hums.historia]
                    lista.extend(vector)
            
            vector2 = [nombre, lista]
            matrizMSHU.append(vector2)
            i += 1
        
        return matrizMSHU    

class Individuo():

    def __init__(self, listaHistorias, dependencias, similitud):
        self.numeroHistorias = len(listaHistorias)
        self.matrizAsignacion = []
        self.microservicios = []
        self.metricas = []
        self.cromosoma = ""
        self.valorFuncion = 0.0
        self.dependencias = dependencias
        self.numero_microservicios=0        
        self.similitud = similitud

    def generarIndividuo(self, listaHistorias, variables, penalizaCx, totalHistorias, totalPuntos):
        self.cromosoma = ""
        self.valorFuncion = 0.0        
        
        for hu in listaHistorias:
            indiceAsignar = randint(0,(self.numeroHistorias-1))
            matriz=[]
            for i in range (0, self.numeroHistorias):
                vector=[]
                if i==indiceAsignar:
                    vector=[hu,1]
                    matriz.append(vector)
                else:
                    vector=[hu,0]
                    matriz.append(vector)                
            
            self.matrizAsignacion.append(matriz)
        self.instanciarMicroservicios(variables, penalizaCx, totalHistorias, totalPuntos)

    def instanciarMicroservicios(self, variables, penalizaCx, totalHistorias, totalPuntos):
        # Identificar los microservicios y asignarles las historias
        self.microservicios=[]
        cromo = ""
        nombre=""
        cont=1
        for j in range(0, self.numeroHistorias):            
            vector=[]
            for fila in self.matrizAsignacion:
                dato = fila[j]
                if dato[1]==1:
                    vecHu = [dato[0]]
                    vector.extend(vecHu)
                    cromo += str(dato[1])
                else:
                    cromo += str(dato[1])
            cromo+="-"
            if len(vector)>0:                
                nombre = "MS" + str(cont)
                ms = [nombre,vector]
                self.microservicios.append(ms)
                cont+=1        
        self.numero_microservicios = cont
        self.cromosoma = cromo

        #Calcular las metricas para la descomposición generada
        metrica = Metrica()
        self.metricas = metrica.calcularMetricasIndividuo(self.microservicios, variables, self.dependencias, penalizaCx, totalHistorias, totalPuntos, self.similitud)
        app = self.metricas[0]
        self.valorFuncion = app.valor_GM
    
    def __str__(self): # __unicode__ en Python 2 
        texto = self.cromosoma + " - " + str(self.valorFuncion) 
        return texto
        
class AlgoritmoGenetico():

    def __init__(self, tamanoPoblacion, iteraciones, hijos, mutaciones, variables, historias, dependencias, penalizaCx, totalHistorias, totalPuntos, similitud):    
        self.tamanoPoblacion = tamanoPoblacion
        self.iteraciones = iteraciones
        self.hijos = hijos
        self.mutaciones = mutaciones
        self.variables = variables
        self.historias = historias
        self.poblacion = []
        self.dependencias = dependencias
        self.penalizaCx = penalizaCx
        self.totalHistorias = totalHistorias
        self.totalPuntos = totalPuntos
        self.similitud = similitud
    
    def generarPoblacion(self):                        
        # for i in range(0, self.tamanoPoblacion):
        #     ind = Individuo(self.historias, self.dependencias, self.similitud)
        #     ind.generarIndividuo(self.historias, self.variables, self.penalizaCx, self.totalHistorias, self.totalPuntos)
        #     vector = [ind]
        #     self.poblacion.extend(vector)     
        cpus = cpu_count()                    
        with Pool(cpus) as p:            
            vector = p.map(self.generarIndividuo, range(0, self.tamanoPoblacion))            
            p.close
            p.join            
            self.poblacion = vector                                     

    def generarIndividuo(self, index):            
        ind = Individuo(self.historias, self.dependencias, self.similitud)
        ind.generarIndividuo(self.historias, self.variables, self.penalizaCx, self.totalHistorias, self.totalPuntos)
        return ind
    
    def generarPoblacionParalelo(self, inicio, fin):                
        for i in range(inicio, fin):
            ind = Individuo(self.historias, self.dependencias, self.similitud)
            ind.generarIndividuo(self.historias, self.variables, self.penalizaCx, self.totalHistorias, self.totalPuntos)
            vector = [ind]
            self.poblacion.extend(vector)                    
            
    def ordenarPoblacion(self):
        lista = self.poblacion
        self.poblacion=[]
        self.poblacion = sorted(lista, key=lambda objeto: objeto.valorFuncion)
    
    def reproducir(self):        
        n = len(self.historias)
        for i in range(0, self.hijos):
            hijo= Individuo(self.historias, self.dependencias, self.similitud)            
            indexPadre = randint(0, self.tamanoPoblacion-1)
            indexMadre = randint(0, self.tamanoPoblacion-1)

            while indexPadre == indexMadre:
                indexMadre = randint(0,self.tamanoPoblacion-1)
            
            padre = self.poblacion[indexPadre]
            madre = self.poblacion[indexMadre]            

            desde = int(n / 2)
            matrizPadre = padre.matrizAsignacion
            matrizMadre = madre.matrizAsignacion
            hijo.matrizAsignacion = []
            #print("---------Desde: " + str(desde))
            for j in range(0, n):
                if j < desde:
                    hijo.matrizAsignacion.append(matrizPadre[j])
                else:
                    hijo.matrizAsignacion.append(matrizMadre[j])
            
            hijo.instanciarMicroservicios(self.variables, self.penalizaCx, self.totalHistorias, self.totalPuntos)

            # print("---------------------------------------------")
            # print("--------------Padre: " + padre.cromosoma)
            # print("--------------Madre: " + madre.cromosoma)
            # print("--------------Hijo: " + hijo.cromosoma) 
            # print("---------------------------------------------")
            vector = [hijo]
            self.poblacion.extend(vector)                    

    def clonarIndividuo(self, individuo):
        ind = copy.deepcopy(individuo)
        return ind

    def mutar(self):
        n = len(self.historias)
        for i in range(0, self.mutaciones):
            indexMutar = randint(0,self.tamanoPoblacion-1)
            mutar= self.poblacion[indexMutar]
            mutado = self.clonarIndividuo(mutar)

            # print("-----------------Inicio")
            # print("--------------Mutar: " + mutar.cromosoma)        
            # print("--------------Mutado: " + mutado.cromosoma)
            
            microservicio = randint(0,n-1)
            historia = randint(0,n-1) 

            # print("--------------microserivicio: " + str(microservicio))
            # print("--------------historia: " + str(historia))

            bitMutar = mutado.matrizAsignacion[historia][microservicio][1]            

            if bitMutar==1:
                mutado.matrizAsignacion[historia][microservicio][1]=0
                bitMutar2 = randint(0,n-1)
                while bitMutar2==microservicio:
                    bitMutar2 = randint(0,n-1)                
                mutado.matrizAsignacion[historia][bitMutar2][1]=1
            
            if bitMutar==0:
                bitMutar2=-1
                for d in range(0, n):
                    if mutado.matrizAsignacion[historia][d][1]==1:
                        bitMutar2 = d
                        break
                mutado.matrizAsignacion[historia][microservicio][1]=1
                mutado.matrizAsignacion[historia][bitMutar2][1]=0
                        
            mutado.instanciarMicroservicios(self.variables, self.penalizaCx, self.totalHistorias, self.totalPuntos)

            # print("------------------Mutacion")
            # print("--------------Mutar: " + mutar.cromosoma)        
            # print("--------------Mutado: " + mutado.cromosoma)
            # print("--------------Ind Mutar: " + str(mutar.valorFuncion))
            # print("--------------MS Mutar: " + str(microservicio))
            # print("--------------Historia Mutar: " + str(historia))
            #print("--------------Ind Mutado: " + str(mutado.valorFuncion))

            vector = [mutado]
            self.poblacion.extend(vector)
    
    def seleccionarMejores(self):                
        self.ordenarPoblacion()
        lista = self.poblacion
        self.poblacion=[]

        for i in range (0, self.tamanoPoblacion):            
            vector = [lista[i]]            
            self.poblacion.extend(vector) 

    def converge(self, convergencia):
        ind = self.poblacion[0]
        valorMejor =round(ind.valorFuncion,4)
        cont=0
        rta= False

        for individuo in self.poblacion:
            valor = round(individuo.valorFuncion, 4)            
            if valor== valorMejor:
                cont+=1
            porcentaje = float(cont) / float(self.tamanoPoblacion)
            porcentaje = round(porcentaje, 2)
            if porcentaje>convergencia:
                rta=True
                break            
        return rta

    def ejecutar(self):
        self.generarPoblacion()        
        #for i in range (0, self.iteraciones):            
        converge=False
        cont=0
        while converge==False and cont < self.iteraciones:
            cont+=1
            self.reproducir()                        
            self.mutar()                        
            self.seleccionarMejores()            
            converge = self.converge(0.1)
        mejor = self.poblacion[0]
        self.iteraciones = cont        
        return mejor     