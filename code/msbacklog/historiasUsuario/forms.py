from django import forms
from django.core.exceptions import ValidationError
from .models import Proyecto, HistoriaUsuario
from django.forms import ModelForm

class ProyectoForm(ModelForm):
    class Meta: 
        model = Proyecto
        fields = ['nombre', 'sigla', 'descripcion', 'usuario', 'es_publico']
        widgets = { 'usuario':forms.HiddenInput(attrs={'readonly':'readonly'}),
                    'nombre':forms.HiddenInput(attrs={'name':'project_name'}),
                    'descripcion':forms.Textarea(),                    
                  }

    def clean(self):
        cleaned_data = super(ProyectoForm, self).clean()

class HistoriaUsuarioForm(ModelForm):
    class Meta: 
        model = HistoriaUsuario
        fields = ['nombre', 'descripcion', 'prioridad', 'puntos_estimados', 'tiempo_estimado',
                    'escenario', 'observaciones', 'proyecto']
        widgets = { 'proyecto':forms.HiddenInput(attrs={'readonly':'readonly'}),                    
                    'descripcion':forms.Textarea(),
                    'escenario':forms.Textarea(),
                    'observaciones':forms.Textarea(),                    
                  }

    def clean(self):
        cleaned_data = super(HistoriaUsuarioForm, self).clean() 