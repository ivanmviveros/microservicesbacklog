# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import spacy
from microservicios.models import Microservicio, Microservicio_Historia
from historiasUsuario.models import HistoriaUsuario, Dependencia_Historia
from metricas.models import Metrica
from random import randint
import math

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
    
    def calcularDistanciaCalls(self, msapp):
        matrizDistancias=[]
        matrizCalls=[]
        listMS = Microservicio.objects.filter(aplicacion= msapp)
        vector=[]
        if listMS:
            for ms in listMS:
                call=0       
                vector = []         
                for ms2 in listMS:
                    if ms.id == ms2.id:
                        call=0
                        #dato = [ms, call]
                        #vector.append(dato)
                    else:
                        historias = Microservicio_Historia.objects.filter(microservicio = ms)
                        historiasmscal = Microservicio_Historia.objects.filter(microservicio = ms2)
                        valor=0
                        for hu in historias:                        
                            for hums in historiasmscal:
                                cont = Dependencia_Historia.objects.filter(historia = hu.historia, dependencia = hums.historia).count()
                                if cont>0:
                                    valor+=1
                        call = valor
                    dato = [ms2, call]                                        
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

    def __init__(self, listaHistorias):
        self.numeroHistorias = len(listaHistorias)
        self.matrizAsignacion = []
        self.microservicios = []
        self.metricas = []
        self.cromosoma = ""
        self.valorFuncion = 0.0
    
    def generarIndividuo(self, listaHistorias, variables):
        self.cromosoma = ""
        self.valorFuncion = 0.0
        self.numeroHistorias = len(listaHistorias)        
        
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
            self.instanciarMicroservicios(variables)

    def instanciarMicroservicios(self, variables):
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
        self.cromosoma = cromo

        # Calcular las metricas para la descomposición generada
        metrica = Metrica()
        self.metricas = metrica.calcularMetricasIndividuo(self.microservicios, variables)
        app = self.metricas[0]
        self.valorFuncion = app.valor_GM
    
    def __str__(self): # __unicode__ en Python 2 
        texto = self.cromosoma + " - " + str(self.valorFuncion) 
        return texto
        
class AlgoritmoGenetico():

    def __init__(self, tamanoPoblacion, iteraciones, hijos, mutaciones, variables, historias):    
        self.tamanoPoblacion = tamanoPoblacion
        self.iteraciones = iteraciones
        self.hijos = hijos
        self.mutaciones = mutaciones
        self.variables = variables
        self.historias = historias
        self.poblacion = []
    
    def generarPoblacion(self):
        poblacion=[]

        for i in range(0, self.tamanoPoblacion):
            ind = Individuo(self.historias)
            ind.generarIndividuo(self.historias, self.variables)
            vector = [ind]
            poblacion.extend(vector)
        
        self.poblacion = poblacion
    
    def ordenarPoblacion(self):
        lista = self.poblacion
        self.poblacion=[]
        self.poblacion = sorted(lista, key=lambda objeto: objeto.valorFuncion)
    
    def reproducir(self):        
        n = len(self.historias)
        for i in range(0, self.hijos):
            hijo= Individuo(self.historias)            
            indexPadre = randint(0, self.tamanoPoblacion-1)
            indexMadre = randint(0, self.tamanoPoblacion-1)

            while indexPadre == indexMadre:
                indexMadre = randint(0,self.tamanoPoblacion-1)
            
            padre = self.poblacion[indexPadre]
            madre = self.poblacion[indexMadre]
            #hijo = padre

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
            
            hijo.instanciarMicroservicios(self.variables)

            """ print("--------------Padre: " + str(padre))
            print("--------------Madre: " + str(madre))
            print("--------------Hijo: " + str(hijo)) """
            vector = [hijo]
            self.poblacion.extend(vector)
    
    def mutar(self):
        n = len(self.historias)
        for i in range(0, self.mutaciones):
            indexMutar = randint(0,self.tamanoPoblacion-1)
            mutar= self.poblacion[indexMutar]
            mutado = mutar 

            microservicio = randint(0,n-1)
            historia = randint(0,n-1) 

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
            
            # print("--------------Ind Mutar: " + str(mutar))
            # print("--------------MS Mutar: " + str(microservicio))
            # print("--------------Historia Mutar: " + str(historia))
            # print("--------------Ind Mutado: " + str(mutado))

            mutado.instanciarMicroservicios(self.variables)

            vector = [mutado]
            self.poblacion.extend(vector)
    
    def seleccionarMejores(self):
        self.ordenarPoblacion()
        lista = self.poblacion
        self.poblacion=[]

        for i in range (0, self.tamanoPoblacion):            
            vector = [lista[i]]
            self.poblacion.extend(vector)
    
    def ejecutar(self):
        self.generarPoblacion()
        for i in range (1, self.iteraciones):            
            self.reproducir()
            self.mutar()
            self.seleccionarMejores()
        mejor = self.poblacion[0]
        return mejor     