# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
def contactos(request):
    return render(request, 'contacto.html')
    
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def landing(request):
    return render(request, 'landing.html')
