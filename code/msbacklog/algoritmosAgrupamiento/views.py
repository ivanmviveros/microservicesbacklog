# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from microservicios.models import MicroservicioApp
from historiasUsuario.models import HistoriaUsuario
from .models import Clustering
from django.http import JsonResponse

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
        mensaje =  "<div id='divHUAsociadas' class='panel panel-primary'>"
        mensaje += "<div class='panel-heading'>Microservices identified</div>"
        mensaje += "<div class='panel-body'>"
        mensaje += "<table class='table table-striped table-bordered'>"
        mensaje += "<thead>"
        mensaje += "<tr>"
        mensaje += "<th>Microservice</th>"
        mensaje += "<th>User stories</th>"
        mensaje += "<th>Avg semantic similarity</th>"
        mensaje += "</tr>"
        mensaje += "</thead>"
        mensaje += "<tbody> "
        i=1
        for ms in dato:
            nombre = "MS" + str(i)            
            mensaje += "<tr>"
            mensaje += "<td>"
            mensaje += nombre
            mensaje += "</td>"
            mensaje += "<td>"
            suma = 0.0
            cont = 0.0
            for dato in ms:                
                historia = dato[0]
                mensaje += historia.identificador + " - " + historia.nombre + "<br>"
                suma += dato[1]
                cont += 1            
            mensaje += "</td>"
            avg = suma / cont
            mensaje += "<td>"
            mensaje += str(round(avg,3)) 
            mensaje += "</td>"
            mensaje += "</tr>"            
            i += 1
        mensaje += "</tbody> "
        mensaje += "</table>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "<div class='box-footer'>"
        mensaje += "<center>"        
        mensaje += "<input type='button' id='btnRequest' name='btnReques' value='Group by Request Metric' class='btn btn-primary'/>"        
        mensaje += "   <input type='button' id='btnSave' name='btnSave' value='Save' class='btn btn-primary'/>"
        mensaje += "   <input type='button' id='btnCancelar' name='btnCancelar' value='Cancel' onclick='regresar()' class='btn btn-primary'/>"
        mensaje += "</center>"
        mensaje += "</div>"        

        #return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': aplicacion, 'lista': lista, 'dato':dato, })
        return JsonResponse({ 'content': { 'message': str(mensaje) } })
    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')