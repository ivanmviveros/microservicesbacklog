# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from microservicios.models import MicroservicioApp
from historiasUsuario.models import HistoriaUsuario
from .models import Clustering

# Create your views here.  
def algoritmoClustering(request, **kwargs):
    if request.method == 'GET':
        aplicacion = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        lista=[]
        return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': aplicacion, 'lista':lista})

    if request.method == 'POST':
        aplicacion = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        historias = HistoriaUsuario.objects.filter(proyecto = aplicacion.proyecto)        
        parametro = request.POST.get('parameter')
        lenguaje = request.POST.get('lenguaje') 
        semantica_en = request.POST.get('semantic')
        modulo = request.POST.get('modulo')

        cluster = Clustering(lenguaje, modulo)
        
        lista = cluster.calcularSimilitud(historias, semantica_en)
        dato = cluster.agruparHistorias(lista, len(historias),float(parametro))
        return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': aplicacion, 'lista': lista, 'dato':dato, })
    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')