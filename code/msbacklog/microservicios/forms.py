from django import forms
from django.core.exceptions import ValidationError
from .models import Microservicio, MicroservicioApp, Microservicio_Historia
from historiasUsuario.models import Proyecto
from django.forms import ModelForm

class MicroservicioAppForm(ModelForm):
    class Meta: 
        model = MicroservicioApp
        fields = ['nombre', 'metodo', 'proyecto', 'descripcion']
        labels = {
            'nombre':'Name', 'descripcion':'Description', 'metodo':'Method', 'proyecto':'Project',
        }
        widgets = {    
            'descripcion':forms.Textarea(),                    
        }

    def clean(self):
        cleaned_data = super(MicroservicioAppForm, self).clean()
    
    def __init__(self, *args, **kwargs):
        super(MicroservicioAppForm, self).__init__(*args, **kwargs)
        initial = kwargs['initial']
        self.fields['proyecto'].queryset = Proyecto.objects.filter(usuario=initial['usuario'])

class MicroservicioForm(ModelForm):
    class Meta: 
        model = Microservicio  
        fields = ['nombre', 'descripcion', 'aplicacion'
        ]
        labels = {
            'nombre':'Name', 'descripcion':'Description',
        }
        widgets = { 
            'aplicacion':forms.HiddenInput(attrs={'readonly':'readonly'}),                                        
            'descripcion':forms.Textarea(),
        }

    def clean(self):
        cleaned_data = super(MicroservicioForm, self).clean()

class MicroservicioHistoriasForm(ModelForm):
    class Meta: 
        model = Microservicio 
        fields = ['descripcion']
        labels = {
            'descripcion':'Description',
        }
        widgets = { 'descripcion':forms.Textarea(),                                        
                  }

    def clean(self):
        cleaned_data = super(MicroservicioHistoriasForm, self).clean()