# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import spacy

# Create your models here.
class Clustering():
    npl=None
    def __init__(self, lenguaje):
        if lenguaje == 'es':
            self.nlp = spacy.load("es_core_news_sm")
        if lenguaje == 'en':
            self.nlp = spacy.load("en_core_news_sm")
    
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

    def calcularSimilitud(self, listaHistorias):
        matrizSimilitud=[]
        textos=[]
        for historia in listaHistorias:
            lista = self.identificarVerbosEntidades(historia)
            textos.append(lista)
        
        for texto in textos:
            hu = texto[0]
            tex = texto[1]
            lem = texto[2]            
            doc1 = self.nlp(lem)            
            similitudes=[hu]

            for tex_hu in textos:                
                hu2 = tex_hu[0]
                texto2 = tex_hu[1]
                lemma2 = tex_hu[2]
                doc2 = self.nlp(lemma2)
                similitud = doc1.similarity(doc2)                
                dicc = [hu2, similitud]
                similitudes.append(dicc)
            
            matrizSimilitud.append(similitudes)
        return matrizSimilitud
    
    def agruparHistorias(self, mastrizSimilitud, n, pAgrupar):
        # for i in range(0, n):
        #     for j in range (i+1, n):
        #         dato = mastrizSimilitud[i][j]
        #         similitud = dato[1]
        #         if similitud > pAgrupar:
        dato = mastrizSimilitud[0]
        return dato





    
