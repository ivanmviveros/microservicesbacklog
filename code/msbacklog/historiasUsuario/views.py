# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .models import Proyecto, HistoriaUsuario, Usuario
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import (
    CreateView,
    UpdateView,    
    DeleteView,
)
from django.views.generic import ListView, DetailView
from django import forms
from .forms import ProyectoForm, HistoriaUsuarioForm
import requests

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
    success_msg = "User Storie saved"

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
        historia = HistoriaUsuario(
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
    success_msg = "User Storie updated"

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
    success_msg = "User Storie Deleted"   

    def get_context_data(self, **kwargs):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])        
        context = super(HistoriaUsuarioDeleteView, self).get_context_data(**kwargs)              
        context['proyecto'] = self.proyecto
        return context
    
    def get_initial(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])        
        return { 'proyecto': self.usuario }
        
    def get_success_url(self):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['id_proyecto'])
        messages.success(self.request, self.success_msg)
        return  '/historias/historias-list/%s' % (self.proyecto.id)

class HistoriaUsuarioDetailView(DetailView):
    model = HistoriaUsuario
    context_object_name = 'historia'