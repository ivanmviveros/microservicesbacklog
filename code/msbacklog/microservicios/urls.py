from django.conf.urls import url
from .views import (
    MicroservicioAppCrearView,
    MicroservicioAppDeleteView,
    MicroservicioAppDetailView,
    MicroservicioAppListView,
    MicroservicioAppEditarView,
    MicroservicioCrearView,
    MicroservicioDeleteView, 
    MicroservicioDetailView, 
    MicroservicioEditarView,
    MicroserviciosHistoriaUdpateView,
    MicroserviciosListView,
)  

urlpatterns = [
        
    url(r'^msapp-list/(?P<id_usuario>\d+)$', MicroservicioAppListView.as_view(), name='list-msapp'),
    url(r'^crear-msapp/(?P<id_usuario>\d+)$', MicroservicioAppCrearView.as_view(), name='create-msapp'),    
    url(r'^editar-msapp/(?P<id_usuario>\d+)/(?P<pk>\d+)$', MicroservicioAppEditarView.as_view(), name='edit-msapp'),
    url(r'^eliminar-msapp/(?P<id_usuario>\d+)/(?P<pk>\d+)$', MicroservicioAppDeleteView.as_view(), name='delete-msapp'),
    url(r'^detalle-msapp/(?P<pk>\d+)$', MicroservicioAppDetailView.as_view(), name='detail-msapp'),

    url(r'^microservicios-list/(?P<id_aplicacion>\d+)$', MicroserviciosListView.as_view(), name='list-microservicios'),
    url(r'^crear-microservicio/(?P<id_aplicacion>\d+)$', MicroservicioCrearView.as_view(), name='create-microservicio'),    
    url(r'^editar-microservicio/(?P<id_aplicacion>\d+)/(?P<pk>\d+)$', MicroservicioEditarView.as_view(), name='edit-microservicio'),
    url(r'^eliminar-microservicio/(?P<id_aplicaicon>\d+)/(?P<pk>\d+)$', MicroservicioDeleteView.as_view(), name='delete-microservicio'),
    url(r'^detalle-microservicio/(?P<pk>\d+)$', MicroservicioDetailView.as_view(), name='detail-microservicio'),    
    #url(r'^cargar-microservicios/(?P<id_aplicacion>\d+)$', microservicios_uploadfile, name='load-microservicios'),
    url(r'^microservicios-historias/(?P<pk>\d+)$', MicroserviciosHistoriaUdpateView.as_view(), name='microservicios-historias'),
]