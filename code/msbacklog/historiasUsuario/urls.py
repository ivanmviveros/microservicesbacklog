from django.conf.urls import url
from . import restviews
from .views import (
    ProyectoCrearView,
    ProyectoDetailView,
    ProyectoEditarView,
    ProyectoListView,        
    ProyectoDeleteView,
    HistoriaUsuarioCrearView,
    HistoriaUsuarioDetailView,
    HistoriaUsuarioEditarView,
    HistoriaUsuarioListView,        
    HistoriaUsuarioDeleteView,
)  

urlpatterns = [
        
    url(r'^proyecto-list/(?P<id_usuario>\d+)$', ProyectoListView.as_view(), name='list-proyecto'),
    url(r'^crear-proyecto/(?P<id_usuario>\d+)$', ProyectoCrearView.as_view(), name='create-proyecto'),    
    url(r'^editar-proyecto/(?P<id_usuario>\d+)/(?P<pk>\d+)$', ProyectoEditarView.as_view(), name='edit-proyecto'),
    url(r'^eliminar-proyecto/(?P<id_usuario>\d+)/(?P<pk>\d+)$', ProyectoDeleteView.as_view(), name='delete-proyecto'),
    url(r'^detalle-proyecto/(?P<pk>\d+)$', ProyectoDetailView.as_view(), name='detail-proyecto'),

    url(r'^historias-list/(?P<id_proyecto>\d+)$', HistoriaUsuarioListView.as_view(), name='list-historias'),
    url(r'^crear-historia/(?P<id_proyecto>\d+)$', HistoriaUsuarioCrearView.as_view(), name='create-historia'),    
    url(r'^editar-historia/(?P<id_proyecto>\d+)/(?P<pk>\d+)$', ProyectoEditarView.as_view(), name='edit-historia'),
    url(r'^eliminar-historia/(?P<id_proyecto>\d+)/(?P<pk>\d+)$', HistoriaUsuarioDeleteView.as_view(), name='delete-historia'),
    url(r'^detalle-historia/(?P<pk>\d+)$', HistoriaUsuarioDetailView.as_view(), name='detail-historia'),    
    
    #Rest Api        
    url(r'^api/proyectos/(?P<id_usuario>[0-9]+)/$', restviews.proyecto_list),
    url(r'^api/crear-proyecto/$', restviews.proyecto_create),
    url(r'^api/detalle-proyecto/(?P<pk>[0-9]+)/$', restviews.proyecto_detail),

    url(r'^api/historias/(?P<id_proyecto>[0-9]+)/$', restviews.historias_list),
    url(r'^api/crear-historia/$', restviews.historia_create),
    url(r'^api/detalle-historia/(?P<pk>[0-9]+)/$', restviews.historia_detail),    

]