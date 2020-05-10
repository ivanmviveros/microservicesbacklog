from django.conf.urls import url
from .views import (
    MetricasEditarView,
)  

urlpatterns = [
            
    url(r'^calcular-metricas/(?P<pk>\d+)$', MetricasEditarView.as_view(), name='calculate-metrics'),    

]