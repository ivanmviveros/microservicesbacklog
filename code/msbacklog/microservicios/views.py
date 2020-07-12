# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from subprocess import call

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .models import MicroservicioApp, Microservicio, Microservicio_Historia
from historiasUsuario.models import Usuario, Proyecto, HistoriaUsuario, Dependencia_Historia
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.views.generic.edit import (
    CreateView,
    UpdateView,    
    DeleteView,
)
from django.views.generic import ListView, DetailView
from django import forms 
from .forms import MicroservicioAppForm, MicroservicioForm, MicroservicioHistoriasForm
from algoritmosAgrupamiento.models import Clustering
from random import randint
import requests

# Create your views here.
class MicroservicioAppListView(ListView):
    model = MicroservicioApp
    context_object_name = 'listaMsapp'

    def get_queryset(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        return MicroservicioApp.objects.filter(proyecto__usuario = self.usuario) 

    def get_context_data(self, **kwargs): 
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])               
        context = super(MicroservicioAppListView, self).get_context_data(**kwargs)      
        context['usuario'] = self.usuario        
        return context    

    def get_initial(self):    
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])            
        return { 'usuario': self.usuario}

class MicroservicioAppCrearView(CreateView):
    model = MicroservicioApp
    form_class = MicroservicioAppForm    
    success_msg = "Microservice App decomposition saved"
    metodo=""    

    def get_context_data(self, **kwargs): 
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        context = super(MicroservicioAppCrearView, self).get_context_data(**kwargs)      
        context['usuario'] = self.usuario        
        return context

    def get_initial(self):    
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])            
        self.proyectos = Proyecto.objects.filter(usuario = self.usuario)               
        return { 'usuario': self.usuario}
    
    def form_valid(self, form):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        msApp = MicroservicioApp(
            nombre = form.cleaned_data['nombre'],
            descripcion = form.cleaned_data['descripcion'],
            metodo = form.cleaned_data['metodo'],
            proyecto = form.cleaned_data['proyecto'],            
        )
        msApp.save()        
        self.metodo = form.cleaned_data['metodo']
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        messages.success(self.request, self.success_msg)        
        return  '/microservicios/msapp-list/%s' % (self.usuario.id)

class MicroservicioAppEditarView(UpdateView):
    model = MicroservicioApp
    form_class = MicroservicioAppForm
    context_object_name = 'msapp'    
    success_msg = "Microservice App decomposition updated"

    def get_context_data(self, **kwargs):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        context = super(MicroservicioAppEditarView, self).get_context_data(**kwargs)              
        context['usuario'] = self.usuario
        return context
    
    def get_initial(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        return { 'usuario': self.usuario }    
    
    def get_success_url(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/msapp-list/%s' % (self.usuario.id)

class MicroservicioAppDeleteView(DeleteView):
    model = MicroservicioApp 
    success_msg = "Microservice App decomposition Deleted"
    protect_msg = "Cannot delete Microservice App decomposition, some relation exists"   

    def get_context_data(self, **kwargs):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        context = super(MicroservicioAppDeleteView, self).get_context_data(**kwargs)              
        context['usuario'] = self.usuario
        return context
    
    def get_initial(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        return { 'usuario': self.usuario }        
        
    def get_success_url(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/msapp-list/%s' % (self.usuario.id)
    
class MicroservicioAppDetailView(DetailView):
    model = MicroservicioApp
    context_object_name = 'msapp'

    def get_context_data(self, **kwargs):
        msapp = get_object_or_404(MicroservicioApp, id=self.kwargs['pk'])
        self.microservicios = Microservicio.objects.filter(aplicacion = msapp)        
        context = super(MicroservicioAppDetailView, self).get_context_data(**kwargs)              
        context['microservicios'] = self.microservicios
        return context
    
    def get_initial(self):
        msapp = get_object_or_404(MicroservicioApp, id=self.kwargs['pk'])
        self.microservicios = Microservicio.objects.filter(aplicacion = msapp)
        return { 'microservicios': self.microservicios }

class MicroserviciosListView(ListView):
    model = Microservicio
    context_object_name = 'listams'

    def get_queryset(self):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])        
        return Microservicio.objects.filter(aplicacion = self.aplicacion) 

    def get_context_data(self, **kwargs): 
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])                  
        context = super(MicroserviciosListView, self).get_context_data(**kwargs)      
        listams = Microservicio.objects.filter(aplicacion = self.aplicacion)
        context['aplicacion'] = self.aplicacion       
        return context
    
    def get_initial(self):    
        self.aplicacion = get_object_or_404(Proyecto, id=self.kwargs['id_aplicacion'])         
        listams = Microservicio.objects.filter(aplicacion = self.aplicacion)                            
        return { 'aplicacion': self.aplicacion, 'listams': listams}

class MicroservicioCrearView(CreateView):
    model = Microservicio
    form_class = MicroservicioForm    
    success_msg = "Microservice saved"
    exists_msg = "Microservice already exists"

    def get_context_data(self, **kwargs): 
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])               
        context = super(MicroservicioCrearView, self).get_context_data(**kwargs)      
        context['aplicacion'] = self.aplicacion        
        return context

    def get_initial(self):    
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])            
        return { 'aplicacion': self.aplicacion}
    
    def form_valid(self, form):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])        
        
        ms = Microservicio(            
            nombre = form.cleaned_data['nombre'],
            descripcion = form.cleaned_data['descripcion'],            
            aplicacion = self.aplicacion,                        
        )
        ms.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/microservicios-list/%s' % (self.aplicacion.id)    

class MicroservicioEditarView(UpdateView):
    model = Microservicio
    form_class = MicroservicioForm
    context_object_name = 'microservicio'    
    success_msg = "Microservice updated"

    def get_context_data(self, **kwargs):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])        
        context = super(MicroservicioEditarView, self).get_context_data(**kwargs)              
        context['aplicacion'] = self.aplicacion
        return context
    
    def get_initial(self):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])        
        return { 'aplicacion': self.aplicacion }    
    
    def get_success_url(self):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/microservicios-list/%s' % (self.aplicacion.id)

class MicroservicioDeleteView(DeleteView):
    model = Microservicio  
    success_msg = "Microservice Deleted"   

    def get_context_data(self, **kwargs):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])        
        context = super(MicroservicioDeleteView, self).get_context_data(**kwargs)              
        context['aplicacion'] = self.aplicacion
        return context
    
    def get_initial(self):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])        
        return { 'aplicacion': self.aplicacion }
        
    def get_success_url(self):
        self.aplicacion = get_object_or_404(MicroservicioApp, id=self.kwargs['id_aplicacion'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/microservicios-list/%s' % (self.aplicacion.id)

class MicroservicioDetailView(DetailView):
    model = Microservicio
    context_object_name = 'microservicio'

    def get_context_data(self, **kwargs):
        microservicio = get_object_or_404(Microservicio, id=self.kwargs['pk'])
        self.historias = Microservicio_Historia.objects.filter(microservicio = microservicio)        
        context = super(MicroservicioDetailView, self).get_context_data(**kwargs)              
        context['historias'] = self.historias
        return context
    
    def get_initial(self):
        microservicio = get_object_or_404(Microservicio, id=self.kwargs['pk'])
        self.historias = Microservicio_Historia.objects.filter(microservicio = microservicio)        
        return { 'historias': self.historias }

class MicroserviciosHistoriaUdpateView(UpdateView):
    model = Microservicio    
    context_object_name = 'microservicio'
    form_class = MicroservicioHistoriasForm
    template_name = 'microservicios/microserviciohistorias_form.html'
    success_msg = "Asociated user stories to microservice  saved."

    def get_context_data(self, **kwargs):               
        self.microservicio = get_object_or_404(Microservicio, id=self.kwargs['pk'])
        self.historias = HistoriaUsuario.objects.order_by('prioridad')
        self.asociadas = Microservicio_Historia.objects.filter(microservicio = self.microservicio).order_by('id')
        context = super(MicroserviciosHistoriaUdpateView, self).get_context_data(**kwargs)              
        context['microservico'] = self.microservicio
        context['historias'] = self.historias
        context['asociadas'] = self.asociadas
        return context
    
    def get_initial(self):        
        self.microservicio = get_object_or_404(Microservicio, id=self.kwargs['pk'])
        self.historias = HistoriaUsuario.objects.order_by('prioridad')
        self.asociadas = Microservicio_Historia.objects.filter(microservicio = self.microservicio).order_by('id')
        return { 'microservicio': self.microservicio, 'historias':self.historias, 'asociadas':self.asociadas }
                
    def form_valid(self, form):
        self.microservicio = get_object_or_404(Microservicio, id=self.kwargs['pk'])        
        Microservicio_Historia.objects.filter(microservicio= self.microservicio).delete()

        if self.request.method == 'POST':
            datos = self.request.POST['itemsSelecciona']
            historias = datos.split(",")

            for h in historias:
                if h!="":
                    item = h.split("-")                    
                    idHistoria = item[0]
                    idHistoria = idHistoria.strip()                    
                    if idHistoria!="":
                        depende = HistoriaUsuario.objects.get(id= int(idHistoria))
                        microservicio_his = Microservicio_Historia(
                            microservicio = self.microservicio,
                            historia = depende
                        )
                        microservicio_his.save()

        return HttpResponseRedirect(self.get_success_url())
        
    def get_success_url(self):
        self.microservicio = get_object_or_404(Microservicio, id=self.kwargs['pk'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/microservicios-list/%s' % (self.microservicio.aplicacion.id)

def microservicesBacklogDiagram(request, **kwargs):
    if request.method == 'GET':
        msapp = get_object_or_404(MicroservicioApp, id=kwargs['pk'])
        listaMS = Microservicio.objects.filter(aplicacion = msapp)

        listaDep = Dependencia_Historia.objects.filter(historia__proyecto = msapp.proyecto)   
        dependencias=[]
        for dephu in listaDep:
            id1= dephu.historia.id
            id2= dephu.dependencia.id
            vector= [id1, id2]
            dependencias.append(vector)

        cluster = Clustering('es', 'sm')
        matrizCalls = cluster.calcularDistanciaCalls(msapp, dependencias)

        vector = msapp.getDataMicroservicesBacklog(matrizCalls)
        nodos= vector[0]
        edjes= vector[1]
        metricas = vector[2]
                                                                                                                                                                                
        return render(request, 'microservicios/microservicesbacklog.html', {'msapp': msapp, 'nodos': nodos, 'ejes': edjes, 'metricas': metricas})