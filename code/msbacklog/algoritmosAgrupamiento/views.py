# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from microservicios.models import MicroservicioApp, Microservicio, Microservicio_Historia
from historiasUsuario.models import HistoriaUsuario
from .models import Clustering
from django.http import JsonResponse

# Create your views here.  
def algoritmoClustering(request, **kwargs):
    if request.method == 'GET':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        lista=[]
        return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': msapp, 'lista':lista})

    if request.method == 'POST':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        historias = HistoriaUsuario.objects.filter(proyecto = msapp.proyecto)        
        parametro = request.POST.get('parameter')
        lenguaje = request.POST.get('lenguaje') 
        semantica_en = request.POST.get('semantic')
        modulo = request.POST.get('modulo')
        token = request.POST.get('token')

        # Borrar las historias de los microservicios
        listMs = Microservicio.objects.filter(aplicacion = msapp)
        for ms in listMs:
            Microservicio_Historia.objects.filter(microservicio=ms).delete()

        #Borrar los microservicios que estaban antes
        if listMs:
            Microservicio.objects.filter(aplicacion = msapp).delete()
        
        # Agrupar las historias 
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
                         
            # Guardar en la base de datos la descomposicion
            micro = Microservicio(
                nombre = nombre,
                numero_historias = cont,
                similitud_semantica = avg,
                aplicacion = msapp
            )
            micro.save()

            for dato in ms:
                hu = dato[0]
                ms_hu = Microservicio_Historia(
                    microservicio = micro,
                    historia = hu
                )
                ms_hu.save()
            i += 1
        mensaje += "</tbody> "
        mensaje += "</table>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "<div class='box-footer'>"
        mensaje += "<center>"
        mensaje += "<form method='post' id='frmClusteringCalls' name='frmClusteringCalls' data-post-url='/algoritmos/clustering_calls/" + str(msapp.id) + "' class='form-horizontal' enctype='multipart/form-data'>" 
        mensaje +=  "<input type='hidden' name='csrfmiddlewaretoken' value='nE6GZ9xyyhCoTAbGBK4ah9L1NEnqO1AL4VoYicImxP5Ru8yYhLwg2waAIqmCrQri' />"
        mensaje += "<input type='hidden' id='msapp' name='msapp' value='" + str(msapp.id) + "'>"
        mensaje += "<input type='hidden' id='param' name='param' value='" + parametro + "'>"
        mensaje += "<input type='hidden' id='leng' name='leng' value='" + lenguaje + "'>"
        mensaje += "<input type='hidden' id='mdlo' name='mdlo' value='" + modulo + "'>"    
        mensaje += "<input type='button' id='btnRequest' name='btnRequest' value='Group by Calls Metric'  onclick='clustercalls()' class='btn btn-primary'/>"                
        mensaje += "   <input type='button' id='btnCancelar' name='btnCancelar' value='Cancel' onclick='regresar()' class='btn btn-primary'/>"
        mensaje += "</form>"        
        mensaje += "</center>"
        mensaje += "</div>"        

        #return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': aplicacion, 'lista': lista, 'dato':dato, })
        return JsonResponse({ 'content': { 'message': str(mensaje) } })
    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')

def clusteringCalls(request, **kwargs):
    if request.method == 'GET':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        lenguaje = request.POST.get('leng') 
        parametro = request.POST.get('param')
        modulo = request.POST.get('mdlo')
        cluster = Clustering(lenguaje, modulo)            
        #datos = cluster.calcularDistanciaCalls(msapp)        
        datos = cluster.calcularDistanciaCoupling(msapp)

        mensaje =  "<div id='divMSCalls' class='panel panel-primary'>"
        mensaje += "<div class='panel-heading'>Clustering Microservices</div>"
        mensaje += "<div class='panel-body'>"
        mensaje += "<table class='table table-striped table-bordered'>"
        mensaje += "<thead>"
        mensaje += "<tr>"
        mensaje += "<th>Microservice</th>"
        mensaje += "<th>Calls</th>"        
        mensaje += "</tr>"
        mensaje += "</thead>"
        mensaje += "<tbody> "
        # mensaje += "<tr>"
        # mensaje += "<td>"
        # mensaje += str(datos)
        # mensaje += "</td>"
        # mensaje += "</tr>"

        for dato in datos:
            mensaje += "<tr>"
            mensaje += "<td>"
            mensaje += str(dato[0])
            mensaje += "</td>"
            for ms in dato[1]:            
                nombre = ms[0].nombre                            
                mensaje += "<td>"
                mensaje += nombre
                mensaje += "</td>"                
                mensaje += "<td>" 
                calls = ms[1]
                mensaje += str(round(calls,3))                
                mensaje += "</td>"                
            mensaje += "</tr>"

        mensaje += "</tbody> "
        mensaje += "</table>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "</div>"
    
        return JsonResponse({ 'content': { 'message': mensaje } })
        #return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': msapp, 'lista':lista})        
    # is_ajax    
    if request.method == 'POST':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        
        lenguaje = request.POST.get('leng') 
        parametro = request.POST.get('param')
        modulo = request.POST.get('mdlo')     

        cluster = Clustering(lenguaje, modulo)            
        datos = cluster.calcularDistanciaCalls()
        mensaje = datos
    
        return JsonResponse({ 'content': { 'message': 'OK' } })
    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')
