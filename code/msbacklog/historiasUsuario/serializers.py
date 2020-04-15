from rest_framework import serializers
from .models import Proyecto, HistoriaUsuario, Dependencia_Historia

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ('id','nombre','descripcion','sigla','fecha_creacion', 
                'es_publico', 'usuario')

class HistoriaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriaUsuario
        fields = ('id','nombre', 'descripcion','prioridad','puntos_estimados',
                  'tiempo_estimado','escenario', 'observaciones', 'fecha_creacion',
                  'proyecto', 'microservicio')  

class Dependencia_HistoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependencia_Historia
        fields = ('id','historia', 'dependencia')