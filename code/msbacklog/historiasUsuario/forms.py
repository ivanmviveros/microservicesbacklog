from django import forms
from django.core.exceptions import ValidationError
from .models import Proyecto, HistoriaUsuario, Dependencia_Historia
from django.forms import ModelForm

class ProyectoForm(ModelForm):    
    class Meta: 
        IDIOMA_CHOICES =( 
            ("en", "English"), 
            ("es", "Spanish"),         
        )        
        model = Proyecto
        
        fields = ['nombre', 'sigla', 'descripcion', 'usuario', 'idioma','es_publico']
        labels = {
            'nombre':'Name', 'sigla':'Abbreviation', 'idioma':'Language', 'descripcion':'Description', 'es_publico':'Is public'
        }
        widgets = { 'usuario':forms.HiddenInput(attrs={'readonly':'readonly'}),                                        
                    'idioma': forms.Select(choices = IDIOMA_CHOICES),
                    'descripcion':forms.Textarea(),                    
        }
        

    def clean(self):
        cleaned_data = super(ProyectoForm, self).clean()

class HistoriaUsuarioForm(ModelForm):
    class Meta: 
        model = HistoriaUsuario  
        fields = ['identificador', 'nombre', 'descripcion', 'prioridad', 'puntos_estimados', 'tiempo_estimado',
                    'escenario', 'observaciones', 'proyecto']
        labels = {
            'identificador':'ID','nombre':'Name', 'prioridad':'Priority', 'descripcion':'Description', 
            'puntos_estimados':'Estimated points', 'tiempo_estimado':'Estimated time', 'escenario':'Scenario',
            'observaciones':'Observations',
        }
        widgets = { 'proyecto':forms.HiddenInput(attrs={'readonly':'readonly'}),                    
                    'descripcion':forms.Textarea(),
                    'escenario':forms.Textarea(),
                    'observaciones':forms.Textarea(),                    
                  }

    def clean(self):
        cleaned_data = super(HistoriaUsuarioForm, self).clean() 

class UploadFileForm(forms.Form):    
    file = forms.FileField()

class HistoriaDependenciasForm(ModelForm):
    class Meta: 
        model = HistoriaUsuario 
        fields = ['escenario']
        labels = {
            'escenario':'Scenario',
        }
        widgets = { 'escenario':forms.Textarea(),                                        
                  }

    def clean(self):
        cleaned_data = super(HistoriaDependenciasForm, self).clean()