from django.conf.urls import url
from .views import (
    algoritmoClustering,
)  

urlpatterns = [
            
    url(r'^clusterin-algortimo/(?P<pk>\d+)$', algoritmoClustering, name='clustering-algoritmo'),    

]