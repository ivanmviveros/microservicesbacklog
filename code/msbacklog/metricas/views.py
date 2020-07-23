# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from microservicios.models import MicroservicioApp, Microservicio, Microservicio_Historia
from historiasUsuario.models import Dependencia_Historia
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
from .forms import MetricasUpdateForm
from .models import Metrica
import requests

# Create your views here.
class MetricasEditarView(UpdateView):
    model = MicroservicioApp
    form_class = MetricasUpdateForm
    context_object_name = 'msapp'  
    template_name = 'metricas/calcularmetricas_form.html'  
    success_msg = "Microservice App metrics were calculated"    

    def get_context_data(self, **kwargs):
        msapp = get_object_or_404(MicroservicioApp, id=self.kwargs['pk'])
        #if msapp.metodo == 3 :
        listaDep = Dependencia_Historia.objects.filter(historia__proyecto = msapp.proyecto)   
        dependencias=[]
        for dephu in listaDep:
            vector= [dephu.historia.id, dephu.dependencia.id]
            dependencias.append(vector)
        
        penalizaCx="2"
        totalHistorias = msapp.proyecto.getNumeroHistorias()
        totalPuntos = msapp.proyecto.getTotalPuntos()

        metrica = Metrica()
        metrica.calcularMetricasMSApp(msapp, dependencias, penalizaCx, totalHistorias, totalPuntos)
        self.microservicios = Microservicio.objects.filter(aplicacion = msapp)        
        context = super(MetricasEditarView, self).get_context_data(**kwargs)              
        context['microservicios'] = self.microservicios
        context['msapp'] = msapp
        return context

    def get_initial(self):
        msapp = get_object_or_404(MicroservicioApp, id=self.kwargs['pk'])        
        #if msapp.metodo == 3 :
        listaDep = Dependencia_Historia.objects.filter(historia__proyecto = msapp.proyecto)   
        dependencias=[]
        for dephu in listaDep:
            vector= [dephu.historia.id, dephu.dependencia.id]
            dependencias.append(vector)

        penalizaCx="2"
        totalHistorias = msapp.proyecto.getNumeroHistorias()
        totalPuntos = msapp.proyecto.getTotalPuntos()

        metrica = Metrica()
        metrica.calcularMetricasMSApp(msapp, dependencias, penalizaCx, totalHistorias, totalPuntos)
        self.microservicios = Microservicio.objects.filter(aplicacion = msapp)
        return { 'microservicios': self.microservicios, 'msapp': msapp }
            
    def get_success_url(self):        
        msapp = get_object_or_404(MicroservicioApp, id=self.kwargs['pk'])
        messages.success(self.request, self.success_msg)
        return  '/microservicios/microservicios-list/%s' % (msapp.proyecto.usuario.id)