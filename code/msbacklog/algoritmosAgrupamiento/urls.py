from django.conf.urls import url
from .views import (
    algoritmoClustering,
    clusteringCalls,
    algoritmoGenetico,
)  

urlpatterns = [
            
    url(r'^clusterin-algortimo/(?P<pk>\d+)$', algoritmoClustering, name='clustering-algoritmo'),
    url(r'^clustering-calls/(?P<pk>\d+)$', clusteringCalls, name='clustering-calls'),    
    url(r'^algortimo-genetico/(?P<pk>\d+)$', algoritmoGenetico, name='algoritmo-genetico'),

]