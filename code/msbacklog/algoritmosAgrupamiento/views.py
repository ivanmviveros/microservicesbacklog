# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from microservicios.models import MicroservicioApp, Microservicio, Microservicio_Historia
from historiasUsuario.models import HistoriaUsuario, Dependencia_Historia
from .models import Clustering, Individuo, AlgoritmoGenetico
from historiasUsuario.models import Proyecto, Usuario
from django.http import JsonResponse
from metricas.models import Metrica
import json
from time import time

# Create your views here.  
def algoritmoClustering(request, **kwargs):
    if request.method == 'GET':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])        
        return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': msapp})

    if request.method == 'POST':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        historias = HistoriaUsuario.objects.filter(proyecto = msapp.proyecto)        
        parametro = request.POST.get('parameter') # parametro de similitud semantecia
        coup_parametro = request.POST.get('coup_parameter')
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
        startime = time()        
        cluster = Clustering(lenguaje, modulo)        
        lista = cluster.identificarEntidadHistorias(historias)
        lista2 = cluster.agruparPorFrecuenciaEntidad(lista, float(parametro), semantica_en)
        dura = time() - startime
        ##lista = cluster.calcularSimilitud(historias, semantica_en)
        ##dato = cluster.agruparHistorias(lista, len(historias),float(parametro))
        mensaje =  "<div id='divHUAsociadas' class='panel panel-primary'>"
        mensaje += "<div class='panel-heading'>Microservices grouped by semantic similarity</div>"
        mensaje += "<div class='panel-body'>"
        mensaje += "<table class='table table-striped table-bordered'>"
        mensaje += "<thead>"
        mensaje += "<tr>"
        mensaje += "<th>Microservice</th>"
        mensaje += "<th>User stories</th>"
        mensaje += "<th>Number of stories</th>"
        mensaje += "</tr>"
        mensaje += "</thead>"
        mensaje += "<tbody> "
        mensaje += "<tr>"
        mensaje += "<td colspan='3'>"
        mensaje += "Microservices: " + str(len(lista2))
        mensaje += "<br>Execution time: " + str(round(dura,3))
        mensaje += "</td>"
        mensaje += "</tr>"

        # for dato in lista:
        #     hu = dato[0]
        #     text = dato[1]
        #     lemma = dato[2]
        #     mensaje += "<tr>"
        #     mensaje += "<td>"
        #     mensaje += hu.identificador + " - " + hu.nombre + "<br>" + hu.descripcion
        #     #mensaje += hu #+ " - " + hu.nombre + "<br>" + hu.descripcion
        #     mensaje += "</td>"            
        #     mensaje += "<td>"
        #     mensaje += str(text)
        #     mensaje += "</td>"
        #     mensaje += "<td>"
        #     mensaje += str(lemma)
        #     mensaje += "</td>"
        #     mensaje += "</tr>"


        i=1
        for ms in lista2:
            nombre = "MS - " + ms[0][1]
            mensaje += "<tr>"
            mensaje += "<td>"
            mensaje += nombre
            mensaje += "</td>"
            mensaje += "<td>"
            suma = 0.0
            cont = 0

            for dato in ms:                
                historia = dato[0]
                mensaje += historia.identificador + " - " + historia.nombre + "<br>"                
                cont += 1            
            mensaje += "</td>"
            #avg = suma / cont
            mensaje += "<td>"
            mensaje += str(cont) 
            mensaje += "</td>"
            mensaje += "</tr>"           
                         
            # Guardar en la base de datos la descomposicion
            micro = Microservicio(
                nombre = nombre,
                numero_historias = cont,
                similitud_semantica = 0,
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
        mensaje += "<input type='hidden' id='coup_param' name='coup_param' value='" + coup_parametro + "'>"    
        mensaje += "<input type='hidden' id='semantic' name='semantic' value='" + semantica_en + "'>"
        mensaje += "<input type='button' id='btnRequest' name='btnRequest' value='Group by Coupling Metrics'  onclick='clustercalls()' class='btn btn-primary'/>"                
        mensaje += "   <input type='button' id='btnCancelar' name='btnCancelar' value='Cancel' onclick='regresar()' class='btn btn-primary'/>"
        mensaje += "</form>"        
        mensaje += "</center>"
        mensaje += "</div>"        

        # Calcular las métricas
        metrica = Metrica()
        metrica.calcularMetricas(msapp)

        #return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': aplicacion, 'lista': lista, 'dato':dato, })
        return JsonResponse({ 'content': { 'message': str(mensaje) } })
    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')

def clusteringCalls(request, **kwargs):
    if request.method == 'GET':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        lenguaje = request.GET.get('leng') 
        parametro = request.GET.get('param')
        modulo = request.GET.get('mdlo')                        
        coup_parametro = request.GET.get('coup_parameter')   
        semantica_en = request.GET.get('semantica')

        print('------ semantica_en: ' +  str(semantica_en))

        cluster = Clustering(lenguaje, modulo) 
        startime = time()                                                    
        #simil_param = (float(parametro) - 0.05)
        simil_param = float(parametro)
        #datos = cluster.calcularDistanciaCoupling(msapp)
        #microservicios = Microservicio.objects.filter(aplicacion = msapp)        
        #listaMs = cluster.agruparMicroservicios(datos, len(microservicios), float(coup_parametro) )
        #matrizMSHU = cluster.generarGrupoMS(listaMs) 
        matrizMSHU = cluster.reAgruparMicroservicios(msapp, float(coup_parametro), simil_param, semantica_en )        
        dura = time() - startime
        # Borrar las historias de los microservicios
        lista = Microservicio.objects.filter(aplicacion = msapp)
        for ms in lista:
            Microservicio_Historia.objects.filter(microservicio=ms).delete()

        #Borrar los microservicios que estaban antes
        if lista:
            Microservicio.objects.filter(aplicacion = msapp).delete()
        
        #numero =0
         # Calcular las métricas        
        
        mensaje =  "<div id='divMSCoupling' class='panel panel-primary'>"
        mensaje += "<div class='panel-heading'>Microservices Grouped by Coupling Metrics</div>"
        mensaje += "<div class='panel-body'>"
        mensaje += "<table class='table table-striped table-bordered'>"
        mensaje += "<thead>"
        mensaje += "<tr>"
        mensaje += "<th>Microservice</th>"
        mensaje += "<th>User Stories</th>"        
        mensaje += "</tr>"
        mensaje += "</thead>"
        mensaje += "<tbody> "
        mensaje += "<tr>"
        mensaje += "<td colspan='2'>"
        mensaje += "Microservices: " + str(len(matrizMSHU))
        mensaje += "<br>Execution time: " + str(round(dura,3))
        mensaje += "<br>Similarity param: " + str(round(simil_param,3))
        mensaje += "</td>"
        mensaje += "</tr>"
        
        for dato in matrizMSHU:
            #nombreMS = dato[0]
            micro= dato[0]
            #cont = len(dato[1])
            mensaje += "<tr>"
            mensaje += "<td>"
            mensaje += micro.nombre
            mensaje += "<br>SIY: "+ str(micro.siy)
            mensaje += "</td>"
            mensaje += "<td>"

            # Guardar en la base de datos la descomposicion
            # micro = Microservicio(
            #     nombre = nombreMS,
            #     numero_historias = cont,                
            #     aplicacion = msapp
            # )
            micro.save()

            for hu in dato[1]:                
                ms_hu = Microservicio_Historia(
                    microservicio = micro,
                    historia = hu
                )
                ms_hu.save()
                mensaje += hu.identificador + " - " + hu.nombre + "<br>"
            mensaje += "</td>"
            mensaje += "</tr>"
        
        mensaje += "</tbody> "
        mensaje += "</table>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "</div>"
        #mensaje += "<div class='box-footer'>"
        #mensaje += "<center>"
        #mensaje += "<input type='button' id='btnReturn' name='btnReturn' value='Return' onclick='regresar()' class='btn btn-primary'/>"
        #mensaje += "</center>"
        #mensaje += "</div>"
        mensaje += "<div class='box-footer'>"
        mensaje += "<center>"
        mensaje += "<form method='post' id='frmClusteringCalls' name='frmClusteringCalls' data-post-url='/algoritmos/clustering_calls/" + str(msapp.id) + "' class='form-horizontal' enctype='multipart/form-data'>" 
        mensaje +=  "<input type='hidden' name='csrfmiddlewaretoken' value='nE6GZ9xyyhCoTAbGBK4ah9L1NEnqO1AL4VoYicImxP5Ru8yYhLwg2waAIqmCrQri' />"
        mensaje += "<input type='hidden' id='msapp' name='msapp' value='" + str(msapp.id) + "'>"
        mensaje += "<input type='hidden' id='param' name='param' value='" + str(simil_param) + "'>"
        mensaje += "<input type='hidden' id='leng' name='leng' value='" + lenguaje + "'>"
        mensaje += "<input type='hidden' id='mdlo' name='mdlo' value='" + modulo + "'>"
        mensaje += "<input type='hidden' id='coup_param' name='coup_param' value='" + coup_parametro + "'>"    
        mensaje += "<input type='hidden' id='semantic' name='semantic' value='" + str(semantica_en) + "'>"
        mensaje += "<input type='button' id='btnRequest' name='btnRequest' value='Group by Coupling Metrics'  onclick='clustercalls()' class='btn btn-primary'/>"                
        mensaje += "   <input type='button' id='btnCancelar' name='btnCancelar' value='Cancel' onclick='regresar()' class='btn btn-primary'/>"
        mensaje += "</form>"        
        mensaje += "</center>"
        mensaje += "</div>"               
       
        # mensaje += "<tr>"
        # mensaje += "<td>"
        # mensaje += str(datos)
        # mensaje += "</td>"
        # mensaje += "</tr>"
        # 
        #
        metrica = Metrica()
        metrica.calcularMetricas(msapp)        
    
        return JsonResponse({ 'content': { 'message': mensaje } })
        #return render(request, 'algoritmosAgrupamiento/clustering.html', {'msapp': msapp, 'lista':lista})        
    # is_ajax    
    if request.method == 'POST':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        
        lenguaje = request.POST.get('leng') 
        parametro = request.POST.get('param')
        modulo = request.POST.get('mdlo')     

        cluster = Clustering(lenguaje, modulo)            
        datos = cluster.calcularDistanciaCalls(msapp)
        mensaje = datos
    
        return JsonResponse({ 'content': { 'message': 'OK' } })
    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')

    # Create your views here.  
def algoritmoGenetico(request, **kwargs):
    if request.method == 'GET':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])              
        return render(request, 'algoritmosAgrupamiento/genetic.html', {'msapp': msapp })
    
    if request.method == 'POST':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])         
        listaHu = HistoriaUsuario.objects.filter(proyecto= msapp.proyecto)

        listaDep = Dependencia_Historia.objects.filter(historia__proyecto = msapp.proyecto)   
        dependencias=[]
        for dephu in listaDep:
            vector= [dephu.historia.id, dephu.dependencia.id]
            dependencias.append(vector)

        startime = time()        
        lenguaje = msapp.proyecto.idioma        
        cluster = Clustering(lenguaje, 'md')         
        similitud = cluster.calcularDiccionarioSimilitud(listaHu, 'lemma')                                       
        dura = time() - startime                        
        print("---- Calcular similitud semantica: " + str(dura))
        
        poblcacion = request.POST.get('poblacion') 
        iteraciones = request.POST.get('iteraciones') 
        hijos = request.POST.get('hijos') 
        mutaciones = request.POST.get('mutaciones')
        penalizaCx = request.POST.get('penalizaCx') 
        variables = request.POST.getlist('objetivo')                 

        
        #ind = Individuo(listaHu, dependencias)
        #ind.generarIndividuo(listaHu, variables)
        totalHistorias = msapp.proyecto.getNumeroHistorias()
        totalPuntos = msapp.proyecto.getTotalPuntos()
        startime = time()
        genetico = AlgoritmoGenetico(int(poblcacion), int(iteraciones), int(hijos), int(mutaciones), variables, listaHu, dependencias, penalizaCx, totalHistorias, totalPuntos, similitud)                        
        #genetico.generarPoblacion()                
        # genetico.reproducir()
        # genetico.mutar()
        # genetico.ordenarPoblacion()     
        #datos = genetico.poblacion
           
        ind = genetico.ejecutar()                
        
        dura = time() - startime
        print("---- Ejecutar algoritmo genetico: " + str(dura))
        
        metricas = ind.metricas
        app = metricas[0]
        datos = metricas[1]        
        # app= msapp

        # Borrar las historias de los microservicios
        lista = Microservicio.objects.filter(aplicacion = msapp)
        for ms in lista:
            Microservicio_Historia.objects.filter(microservicio=ms).delete()

        #Borrar los microservicios que estaban antes
        if lista:
            Microservicio.objects.filter(aplicacion = msapp).delete()

        msapp.tiempo_estimado_desarrollo = app.tiempo_estimado_desarrollo
        msapp.coupling = app.coupling
        msapp.aist = app.aist
        msapp.adst = app.adst
        msapp.siyt = app.siyt
        
        msapp.cohesion = app.cohesion
        msapp.wsict = app.wsict

        msapp.avg_calls = app.avg_calls
        msapp.avg_requet = app.avg_request
        msapp.valor_GM = ind.valorFuncion
        msapp.numero_microservicios = app.numero_microservicios 
        msapp.complejidad_cognitiva = app.complejidad_cognitiva
        msapp.similitud_semantica = app.similitud_semantica

        msapp.save()

        mensaje =  "<div id='divGenetico' class='panel panel-primary'>"
        mensaje += "<div class='panel-heading'>Microservices Grouped by Genetic Programming</div>"
        mensaje += "<div class='panel-body'>"
        mensaje += "<table class='table table-striped table-bordered'>"
        mensaje += "<thead>"
        mensaje += "<tr>"
        mensaje += "<th>Microservice</th>"
        mensaje += "<th>User Stories</th>"        
        mensaje += "</tr>"
        mensaje += "</thead>"
        mensaje += "<tbody> "
        mensaje += "<tr>"
        mensaje += "<td>"
        mensaje += "Metrics:"
        mensaje += "</td>"
        mensaje += "<td>"
        mensaje += "Execution time: " + str(round(dura,3)) + "<br>"
        mensaje += "Iterations: " + str(genetico.iteraciones) + "<br>"
        mensaje += "Coupling: " + str(round(app.coupling,3)) + "<br>"
        mensaje += "Cohesion: " + str(round(app.cohesion,3)) + "<br>"
        mensaje += "Wsict: " + str(app.wsict) + "<br>"        
        mensaje += "Microservices: " + str(app.numero_microservicios) + "<br>"
        mensaje += "Cognitive Complexity: " + str(round(app.complejidad_cognitiva,3)) + "<br>"
        mensaje += "Semantic similarity: " + str(round(app.similitud_semantica,3)) + "<br>"
        mensaje += "GM: " + str(round(app.valor_GM,3)) + "<br>"
        #mensaje += "Cromosoma: " + ind.cromosoma + "<br>"
        mensaje += "</td>"
        mensaje += "</tr>"         

        for dato in datos:            
            # mensaje += "<tr>"
            # #for hums in dato:
            # mensaje += "<td>"
            # #mensaje += hums[0].identificador + "-" + str(hums[1])
            # mensaje += dato.cromosoma + " - " + str(dato.valorFuncion)
            # mensaje += "</td>"
            # mensaje += "</tr>"
            
            micro = dato[0]
            micro.aplicacion = msapp
            nombreMS = micro.nombre
            micro.save()

            mensaje += "<tr>"
            mensaje += "<td>"
            mensaje += nombreMS + "<BR>"
            mensaje += "historias: " + str(micro.numero_historias) + "<BR>"
            mensaje += "puntos: " + str(micro.total_puntos) + "<BR>"
            mensaje += "Dev. Time: " + str(micro.tiempo_estimado_desarrollo) + "<BR>"
            mensaje += "ais: " + str(micro.ais) + "<BR>"
            mensaje += "ads: " + str(micro.ads) + "<BR>"
            mensaje += "siy: " + str(micro.siy) + "<BR>"
            mensaje += "lack: " + str(micro.lack) + "<BR>"
            mensaje += "Cohesion: " + str(round(micro.grado_cohesion,3)) + "<BR>"
            mensaje += "calls: " + str(micro.calls) + "<BR>"
            mensaje += "request: " + str(micro.request) + "<BR>"
            mensaje += "</td>"
            mensaje += "<td>"                        

            for hu in dato[1]:                
               ms_hu = Microservicio_Historia(
                   microservicio = micro,
                   historia = hu
               )
               ms_hu.save()
               mensaje += hu.identificador + " - " + hu.nombre + "<br>"
            mensaje += "</td>"
            mensaje += "</tr>"

        # i=0
        # for dato in genetico.poblacion:
        #     mensaje += "<tr>"
        #     mensaje += "<td colspan='2'>"
        #     #mensaje += hums[0].identificador + "-" + str(hums[1])
        #     mensaje += dato.cromosoma + " - " + str(dato.valorFuncion)
        #     mensaje += "</td>"
        #     mensaje += "</tr>"
        #     i+=1
        #     if i==12:
        #         break
        
        mensaje += "</tbody> "
        mensaje += "</table>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "</div>"
        mensaje += "<div class='box-footer'>"
        mensaje += "<center>"        
        mensaje += "<input type='button' id='btnReturn' name='btnReturn' value='Return' onclick='regresar()' class='btn btn-primary'/>"
        mensaje += "</center>"
        mensaje += "</div>"
        
        return JsonResponse({ 'content': { 'message': mensaje } })

    messages.success(request, 'Error in GET method')
    return render(request, 'index.html')

def compararDescomposiciones(request, **kwargs):
    if request.method == 'GET':
        usuario = get_object_or_404(Usuario, id=kwargs['pk'])
        proyectos = Proyecto.objects.filter(usuario= usuario)        
        return render(request, 'algoritmosAgrupamiento/compare.html', {'proyectos': proyectos, 'usuario':usuario})
    
    if request.method == 'POST':
        idProyecto = request.POST.get('proyecto')         
        proyecto = get_object_or_404(Proyecto, id=idProyecto)
        listaMSApp = MicroservicioApp.objects.filter(proyecto= proyecto).order_by('valor_GM')

        if listaMSApp:

            mensaje =  "<div id='divMetrics' class='panel panel-primary'>"
            mensaje += "<div class='panel-heading'>Microservices Decompositions Metrics</div>"
            mensaje += "<div class='panel-body'>"
            mensaje += "<table id='tblMetricas' class='table table-striped table-bordered'>"
            mensaje += "<thead>"
            mensaje += "<tr>"
            mensaje += "<th>Methods</th>"
            mensaje += "<th title='Number of microservices'>N</th>"
            mensaje += "<th title='Total absolute importance between microservices '>AisT</th>"
            mensaje += "<th title='Total absolute dependence between microservices '>AdsT</th>"
            mensaje += "<th title='Total microservices interdependences'>SiyT</th>"
            mensaje += "<th title='Total coupling'>CpT</th>"
            mensaje += "<th title='Total cohesion'>CohT</th>"  
            mensaje += "<th title='Cognitive complexity'>CxT</th>"      
            mensaje += "<th title='Total microservice interfaz count'>WsicT</th>"
            mensaje += "<th title='Granularity metric'>GM</th>"            
            #mensaje += "<th title='Highest estimated points'>Max. Points</th>"
            mensaje += "<th title='Avarege of calls between microservices'>Avg. Calls</th>"
            mensaje += "<th title='Highest estimated development time'>Dev. Time</th>"            
            mensaje += "</tr>"
            mensaje += "</thead>"
            mensaje += "<tbody> "

            for msapp in listaMSApp:
                
                if msapp.numero_microservicios == None:
                    msapp.numero_microservicios=0
                if msapp.aist == None:
                    msapp.aist=0
                if msapp.adst == None:
                    msapp.adst=0
                if msapp.siyt == None:
                    msapp.siyt=0
                if msapp.coupling == None:
                    msapp.coupling=0
                if msapp.cohesion == None:
                    msapp.cohesion=0
                if msapp.complejidad_cognitiva == None:
                    msapp.complejidad_cognitiva=0
                if msapp.wsict == None:
                    msapp.wsict=0
                if msapp.valor_GM == None:
                    msapp.valor_GM=0
                if msapp.avg_calls == None:
                    msapp.avg_calls=0
                if msapp.tiempo_estimado_desarrollo == None:
                    msapp.tiempo_estimado_desarrollo=0                

                mensaje += "<tr align='right'>"
                mensaje += "<td align='left'>" + msapp.nombre + "</td>"
                mensaje += "<td aling='rigth'>" + str(msapp.numero_microservicios) + "</td>"
                mensaje += "<td>" + str(round(msapp.aist,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.adst,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.siyt,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.coupling,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.cohesion,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.complejidad_cognitiva,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.wsict,2)) + "</td>"                
                mensaje += "<td>" + str(round(msapp.valor_GM,2)) + "</td>"                
                #mensaje += "<td>" + str(round(msapp.puntos,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.avg_calls,2)) + "</td>"
                mensaje += "<td>" + str(round(msapp.tiempo_estimado_desarrollo,2)) + "</td>"                
                mensaje += "</tr>"
            
            mensaje += "</tbody> "
            mensaje += "</table>"
            mensaje += "</div>"
            mensaje += "</div>"
            mensaje += "</div>"
            mensaje += "<div class='box-footer'>"
            mensaje += "<center>"        
            mensaje += "<input type='button' id='btnReturn' name='btnReturn' value='Return' onclick='regresar()' class='btn btn-primary'/>"
            mensaje += "</center>"
            mensaje += "</div>"            
            mensaje += "<script>"
            mensaje += "$(document).ready(function() {"
            mensaje += "$('#tblMetricas').DataTable({"
            mensaje += "'dom': 'Bfrtip', "
            mensaje += " });"
            mensaje += "} );"
            mensaje += "</script>"
        
        else:
            mensaje = "There are not microservices decompositions."
        
        return JsonResponse({ 'content': { 'message': mensaje } })


@csrf_exempt
def algoritmoGeneticoInteroperabilidad(request, **kwargs):
    PRIORIDADES = ['Very low', 'Low', 'Medium', 'High', 'Very high']

    if request.method == "GET":
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        microservicios = Microservicio.objects.filter(aplicacion = msapp)
        data = []

        for microservicio in microservicios:
            data.append(microservicio.get_json())
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        body_unicode = request.body.decode('ascii', 'ignore').encode('ascii', 'ignore').decode('utf-8')
        json_data = json.loads(body_unicode)
        proyecto = Proyecto.objects.create(nombre=json_data["userStories"][0].get("project","Interoperabilidad"), usuario=Usuario.objects.first())
        msapp = MicroservicioApp.objects.create(nombre=json_data["userStories"][0].get("project","Interoperabilidad"), proyecto=proyecto)
        historias_crear = []
        for historia in json_data["userStories"]:
            historias_crear.append(
                HistoriaUsuario(
                    identificador=historia["id"],
                    nombre=historia["id"],
                    descripcion=historia.get("name"),
                    prioridad=PRIORIDADES.index(historia.get("priority",'Low'))+1,
                    puntos_estimados=historia.get("points",1),
                    tiempo_estimado=historia.get("tiempo_estimado",1),
                    proyecto=proyecto,
                    observaciones=historia.get("actor","")
            ))
        HistoriaUsuario.objects.bulk_create(historias_crear)

        listaHu = HistoriaUsuario.objects.filter(proyecto=msapp.proyecto)

        dependencias_crear = []
        for historia in json_data["userStories"]:
            for dependencia in historia["dependencies"]:
                dependencias_crear.append(
                    Dependencia_Historia(
                        historia=HistoriaUsuario.objects.get(identificador=historia["id"], proyecto=proyecto),
                        dependencia=HistoriaUsuario.objects.get(identificador=dependencia["id"], proyecto=proyecto)
                    )
                )
        Dependencia_Historia.objects.bulk_create(dependencias_crear)


        listaDep = Dependencia_Historia.objects.filter(historia__proyecto=msapp.proyecto)
        dependencias = []
        for dephu in listaDep:
            vector = [dephu.historia.id, dephu.dependencia.id]
            dependencias.append(vector)


        startime = time()
        lenguaje = msapp.proyecto.idioma
        cluster = Clustering(lenguaje, 'md')
        similitud = cluster.calcularDiccionarioSimilitud(listaHu, 'lemma')
        dura = time() - startime
        print("---- Calcular similitud semantica: " + str(dura))

        poblcacion = json_data.get('poblacion',100)
        iteraciones = json_data.get('iteraciones',10)
        hijos = json_data.get('hijos',10)
        mutaciones = json_data.get('mutaciones',5)
        penalizaCx = json_data.get('penalizaCx', 2)
        #
        # <option value="coupling">Coupling</option>
        # <option value="cohesion">Cohesion</option>
        # <option value="complexity">Complexity</option>
        # <option value="wsict">User stories  (WSICT)</option>
        # <option value="semantic">Semantic Similarity</option>
        variables = json_data.get('objetivo',"semantic")

        totalHistorias = msapp.proyecto.getNumeroHistorias()
        totalPuntos = msapp.proyecto.getTotalPuntos()
        startime = time()
        genetico = AlgoritmoGenetico(int(poblcacion), int(iteraciones), int(hijos), int(mutaciones), variables, listaHu, dependencias, penalizaCx, totalHistorias, totalPuntos, similitud)

        ind = genetico.ejecutar()

        dura = time() - startime
        print("---- Ejecutar algoritmo genetico: " + str(dura))

        metricas = ind.metricas
        app = metricas[0]
        datos = metricas[1]
        # app= msapp

        # Borrar las historias de los microservicios
        lista = Microservicio.objects.filter(aplicacion=msapp)
        for ms in lista:
            Microservicio_Historia.objects.filter(microservicio=ms).delete()

        # Borrar los microservicios que estaban antes
        if lista:
            Microservicio.objects.filter(aplicacion=msapp).delete()

        msapp.tiempo_estimado_desarrollo = app.tiempo_estimado_desarrollo
        msapp.coupling = app.coupling
        msapp.aist = app.aist
        msapp.adst = app.adst
        msapp.siyt = app.siyt

        msapp.cohesion = app.cohesion
        msapp.wsict = app.wsict

        msapp.avg_calls = app.avg_calls
        msapp.avg_requet = app.avg_request
        msapp.valor_GM = ind.valorFuncion
        msapp.numero_microservicios = app.numero_microservicios
        msapp.complejidad_cognitiva = app.complejidad_cognitiva
        msapp.similitud_semantica = app.similitud_semantica

        msapp.save()

        for dato in datos:
            micro = dato[0]
            micro.aplicacion = msapp
            micro.save()

            for hu in dato[1]:
                ms_hu = Microservicio_Historia(
                        microservicio=micro,
                        historia=hu
                )
                ms_hu.save()
                # mensaje += hu.identificador + " - " + hu.nombre + "<br>"

        return JsonResponse({'result': "{0}://{1}{2}".format(request.scheme, request.get_host(), reverse_lazy('algoritmos:algoritmo-genetico-interoperabilidad', kwargs={"pk":msapp.pk}))})

    return JsonResponse({'result':''})


