# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from subprocess import call

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .models import Proyecto, HistoriaUsuario, Usuario, Dependencia_Historia
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
from .forms import ProyectoForm, HistoriaUsuarioForm, UploadFileForm, HistoriaDependenciasForm
import requests
import csv
import os

# Create your views here.
def contactos(request):
    return render(request, 'contacto.html')
    
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def landing(request):
    return render(request, 'landing.html')

class ProyectoListView(ListView):
    model = Proyecto
    context_object_name = 'listaProyecto'

    def get_queryset(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        return Proyecto.objects.filter(usuario=self.usuario)

    def get_context_data(self, **kwargs): 
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])               
        context = super(ProyectoListView, self).get_context_data(**kwargs)      
        context['usuario'] = self.usuario        
        return context    

    def get_initial(self):    
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])            
        return { 'usuario': self.usuario}

class ProyectoCrearView(CreateView):
    model = Proyecto
    form_class = ProyectoForm    
    success_msg = "Project saved"

    def get_context_data(self, **kwargs): 
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])               
        context = super(ProyectoCrearView, self).get_context_data(**kwargs)      
        context['usuario'] = self.usuario        
        return context

    def get_initial(self):    
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])            
        return { 'usuario': self.usuario}
    
    def form_valid(self, form):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        proyecto = Proyecto(
            nombre = form.cleaned_data['nombre'],
            descripcion = form.cleaned_data['descripcion'],
            sigla = form.cleaned_data['sigla'],
            es_publico = form.cleaned_data['es_publico'],
            usuario = self.usuario,                        
        )
        proyecto.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        messages.success(self.request, self.success_msg)
        return  '/historias/proyecto-list/%s' % (self.usuario.id)    

class ProyectoEditarView(UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    context_object_name = 'proyecto'    
    success_msg = "Proyect updated"

    def get_context_data(self, **kwargs):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        context = super(ProyectoEditarView, self).get_context_data(**kwargs)              
        context['usuario'] = self.usuario
        return context
    
    def get_initial(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        return { 'usuario': self.usuario }    
    
    def get_success_url(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        messages.success(self.request, self.success_msg)
        return  '/historias/proyecto-list/%s' % (self.usuario.id)

class ProyectoDeleteView(DeleteView):
    model = Proyecto 
    success_msg = "Project Deleted"
    protect_msg = "Cannot delete Project, some relation exists"   

    def get_context_data(self, **kwargs):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        context = super(ProyectoDeleteView, self).get_context_data(**kwargs)              
        context['usuario'] = self.usuario
        return context
    
    def get_initial(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])        
        return { 'usuario': self.usuario }        
        
    def get_success_url(self):
        self.usuario = get_object_or_404(Usuario, id=self.kwargs['id_usuario'])
        messages.success(self.request, self.success_msg)
        return  '/historias/proyecto-list/%s' % (self.usuario.id)
    
class ProyectoDetailView(DetailView):
    model = Proyecto
    context_object_name = 'proyecto'

class HistoriaUsuarioListView(ListView):
    model = HistoriaUsuario
    context_object_name = 'listaHistorias'

    def get_queryset(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])                      
        return HistoriaUsuario.objects.filter(proyecto = self.proyecto) 

    def get_context_data(self, **kwargs): 
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])               
        context = super(HistoriaUsuarioListView, self).get_context_data(**kwargs)      
        context['proyecto'] = self.proyecto        
        return context
    
    def get_initial(self):    
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])            
        return { 'proyecto': self.proyecto}

class HistoriaUsuarioCrearView(CreateView):
    model = HistoriaUsuario
    form_class = HistoriaUsuarioForm    
    success_msg = "User Story saved"
    exists_msg = "User Story already exists"

    def get_context_data(self, **kwargs): 
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])               
        context = super(HistoriaUsuarioCrearView, self).get_context_data(**kwargs)      
        context['proyecto'] = self.proyecto        
        return context

    def get_initial(self):    
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])            
        return { 'proyecto': self.proyecto}
    
    def form_valid(self, form):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])
        try:
            historia = HistoriaUsuario.objects.get(identificador=form.cleaned_data['identificador'])
            messages.error(self.request, self.exists_msg)
        except HistoriaUsuario.DoesNotExist:
            historia = HistoriaUsuario(
                identificador = form.cleaned_data['identificador'],
                nombre = form.cleaned_data['nombre'],
                descripcion = form.cleaned_data['descripcion'],
                prioridad = form.cleaned_data['prioridad'],
                puntos_estimados = form.cleaned_data['puntos_estimados'],
                tiempo_estimado = form.cleaned_data['tiempo_estimado'],
                escenario = form.cleaned_data['escenario'],
                observaciones = form.cleaned_data['observaciones'],
                proyecto = self.proyecto,                        
            )
            historia.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])
        messages.success(self.request, self.success_msg)
        return  '/historias/historias-list/%s' % (self.proyecto.id)    

class HistoriaUsuarioEditarView(UpdateView):
    model = HistoriaUsuario
    form_class = HistoriaUsuarioForm
    context_object_name = 'historia'    
    success_msg = "User Story updated"

    def get_context_data(self, **kwargs):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])        
        context = super(HistoriaUsuarioEditarView, self).get_context_data(**kwargs)              
        context['proyecto'] = self.proyecto
        return context
    
    def get_initial(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])        
        return { 'proyecto': self.proyecto }    
    
    def get_success_url(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])
        messages.success(self.request, self.success_msg)
        return  '/historias/historias-list/%s' % (self.proyecto.id)

class HistoriaUsuarioDeleteView(DeleteView):
    model = HistoriaUsuario 
    success_msg = "User Story Deleted"   

    def get_context_data(self, **kwargs):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])        
        context = super(HistoriaUsuarioDeleteView, self).get_context_data(**kwargs)              
        context['proyecto'] = self.proyecto
        return context
    
    def get_initial(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])        
        return { 'proyecto': self.proyecto }
        
    def get_success_url(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])
        messages.success(self.request, self.success_msg)
        return  '/historias/historias-list/%s' % (self.proyecto.id)

class HistoriaUsuarioDetailView(DetailView):
    model = HistoriaUsuario
    context_object_name = 'historia'

def historiaUsuario_uploadfile(request, **kwargs):            
    proyectoCarga = get_object_or_404(Proyecto, id= kwargs['id_proyecto'])
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            #fname = 'historias-' + str(proyectoCarga.id) + '.cvs'
            #call('sudo touch -m ' + fname)
            fname = 'historias-load.cvs'
            with open(fname,'wb+') as destino:
                for chunk in f.chunks():
                    destino.write(chunk)
            destino.close()
            with open(fname, encoding='utf-8') as cvsfile:
                reader = csv.DictReader(cvsfile)
                cont=0
                existen=0
                for row in reader:
                    try:
                        historia = HistoriaUsuario.objects.get(identificador = row['id'])
                        existen = existen + 1                        
                    except HistoriaUsuario.DoesNotExist:
                        historia_add = HistoriaUsuario(
                            identificador = row['id'],
                            nombre = row['name'],
                            descripcion = row['description'],
                            prioridad = row['priority'],
                            puntos_estimados = row['points'],
                            tiempo_estimado = row['time'],
                            escenario = row['scenario'],
                            observaciones = row['observations'],
                            proyecto = proyectoCarga,                        
                        )
                        historia_add.save()            
                        cont = cont +1                                                                        
                mensaje = 'User stories saved: ' + str(cont) + ' \n' + 'User stories already exist: ' + str(existen)
                messages.success(request, mensaje)            
            #os.remove(fname)
            #all('sudo rm ' + fname)
            cvsfile.close()            
            return HttpResponseRedirect('/historias/historias-list/%s' % (proyectoCarga.id),{'messages':messages})
    else:        
        form = UploadFileForm()    
    return render(request, 'historiasUsuario/historiausuario_upload.html', {'form': form, 'proyecto':proyectoCarga})

class HistoriaDependenciaUdpateView(UpdateView):
    model = HistoriaUsuario
    form_class = HistoriaDependenciasForm
    context_object_name = 'historia'
    template_name = 'historiasUsuario/historiadependencia_form.html'
    success_msg = "User story dependencies saved."

    def get_context_data(self, **kwargs):               
        self.historia = get_object_or_404(HistoriaUsuario, id=self.kwargs['pk'])
        self.historias = HistoriaUsuario.objects.order_by('prioridad')
        self.dependencias = Dependencia_Historia.objects.filter(historia = self.historia).order_by('id')
        context = super(HistoriaDependenciaUdpateView, self).get_context_data(**kwargs)              
        context['historia'] = self.historia
        context['historias'] = self.historias
        context['dependencias'] = self.dependencias
        return context
    
    def get_initial(self):        
        self.historia = get_object_or_404(HistoriaUsuario, id=self.kwargs['pk'])
        self.historias = HistoriaUsuario.objects.order_by('prioridad')
        self.dependencias = Dependencia_Historia.objects.filter(historia = self.historia).order_by('id')
        return { 'historia': self.historia, 'historias':self.historias, 'dependencias':self.dependencias }
                
    def form_valid(self, form):
        self.historia = get_object_or_404(HistoriaUsuario, id=self.kwargs['pk'])
        self.historia.escenario = form.cleaned_data['escenario']
        self.historia.save()

        Dependencia_Historia.objects.filter(historia= self.historia).delete()

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
                        dependencia_his = Dependencia_Historia(
                            historia = self.historia,
                            dependencia = depende
                        )
                        dependencia_his.save()

        return HttpResponseRedirect(self.get_success_url())
        
    def get_success_url(self):
        self.historia = get_object_or_404(HistoriaUsuario, id=self.kwargs['pk'])
        messages.success(self.request, self.success_msg)
        return  '/historias/historias-list/%s' % (self.historia.proyecto.id)



