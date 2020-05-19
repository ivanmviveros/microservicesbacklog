# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import spacy

# Create your models here.
class Clustering():
    npl=None
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
        
