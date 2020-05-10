from django import forms
from django.core.exceptions import ValidationError
from microservicios.models import MicroservicioApp
from django.forms import ModelForm

class MetricasUpdateForm(ModelForm):
    class Meta: 
        model = MicroservicioApp
        fields = ['nombre','tiempo_estimado_desarrollo', 'coupling', 'aist', 'adst', 'siyt', 'cohesion', 'wsict', 
            'avg_calls', 'avg_request', 'valor_GM', 'numero_microservicios'
        ]        
        widgets = {    
            'nombre':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'tiempo_estimado_desarrollo':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'coupling':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'aist':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'adst':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'siyt':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'cohesion':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'wsict':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'avg_calls':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'avg_request':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'valor_GM':forms.HiddenInput(attrs={'readonly':'readonly'}),
            'numero_microservicios':forms.HiddenInput(attrs={'readonly':'readonly'}),            
        }

    def clean(self):
        cleaned_data = super(MetricasUpdateForm, self).clean()

