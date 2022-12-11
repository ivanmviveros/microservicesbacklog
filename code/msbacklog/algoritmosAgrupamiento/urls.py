from django.conf.urls import url
from .views import (
    algoritmoClustering,
    clusteringCalls,
    algoritmoGenetico,
    compararDescomposiciones, algoritmoGeneticoInteroperabilidad,
)  

urlpatterns = [
            
    url(r'^clusterin-algortimo/(?P<pk>\d+)$', algoritmoClustering, name='clustering-algoritmo'),
    url(r'^clustering-calls/(?P<pk>\d+)$', clusteringCalls, name='clustering-calls'),    
    url(r'^algortimo-genetico/(?P<pk>\d+)$', algoritmoGenetico, name='algoritmo-genetico'),
    url(r'^compare-descompositions/(?P<pk>\d+)$', compararDescomposiciones, name='compare-descompositions'),
    url(r'^algortimo-genetico-interoperabilidad$', algoritmoGeneticoInteroperabilidad, name='algoritmo-genetico-interoperabilidad'),
    url(r'^algortimo-genetico-interoperabilidad/(?P<pk>\d+)$', algoritmoGeneticoInteroperabilidad, name='algoritmo-genetico-interoperabilidad'),
]
