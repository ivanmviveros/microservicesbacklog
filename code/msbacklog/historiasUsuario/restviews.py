from django.shortcuts import render
from .models import Proyecto, HistoriaUsuario
from .serializers import ProyectoSerializer, HistoriaUsuarioSerializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
# Create your views here.

# Proyecto
# Obtener el listado de los proyectos
@csrf_exempt
def proyecto_list(request, id_usuario):    
    if request.method == 'GET':
        proyectos = Proyecto.objects.filter(usuario= id_usuario)
        serializer = ProyectoSerializer(proyectos, many=True)
        return JsonResponse(serializer.data, safe=False)

# Crear un Proyecto
@csrf_exempt
def proyecto_create(request):    
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProyectoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

# Obtener, actualizar o borrar un proyecto
@csrf_exempt
def proyecto_detail(request, pk):    
    try:
        proyecto = Proyecto.objects.get(pk=pk)
    except Proyecto.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ProyectoSerializer(proyecto)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ProyectoSerializer(proyecto, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        proyecto.delete()
        return HttpResponse(status=204)

# Historia de Usuaio
# Obtener el listado de las historias de usuario de un proyecto
@csrf_exempt
def historias_list(request, id_proyecto):    
    if request.method == 'GET':
        historias = HistoriaUsuario.objects.filter(proyecto= id_proyecto)
        serializer = HistoriaUsuarioSerializer(historias, many=True)
        return JsonResponse(serializer.data, safe=False)

# Crear una historia de usuario
@csrf_exempt
def historia_create(request):    
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = HistoriaUsuarioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

# Obtener, actualizar o borrar un proyecto
@csrf_exempt
def historia_detail(request, pk):    
    try:
        historia = HistoriaUsuario.objects.get(pk=pk)
    except HistoriaUsuario.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = HistoriaUsuarioSerializer(historia)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = HistoriaUsuarioSerializer(historia, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        historia.delete()
        return HttpResponse(status=204)