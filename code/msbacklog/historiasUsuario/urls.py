from django.conf.urls import url
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
    historiaUsuario_uploadfile,
    HistoriaDependenciaUdpateView,
)  

urlpatterns = [
        
    url(r'^proyecto-list/(?P<id_usuario>\d+)$', ProyectoListView.as_view(), name='list-proyecto'),
    url(r'^crear-proyecto/(?P<id_usuario>\d+)$', ProyectoCrearView.as_view(), name='create-proyecto'),    
    url(r'^editar-proyecto/(?P<id_usuario>\d+)/(?P<pk>\d+)$', ProyectoEditarView.as_view(), name='edit-proyecto'),
    url(r'^eliminar-proyecto/(?P<id_usuario>\d+)/(?P<pk>\d+)$', ProyectoDeleteView.as_view(), name='delete-proyecto'),
    url(r'^detalle-proyecto/(?P<pk>\d+)$', ProyectoDetailView.as_view(), name='detail-proyecto'),

    url(r'^historias-list/(?P<id_proyecto>\d+)$', HistoriaUsuarioListView.as_view(), name='list-historias'),
    url(r'^crear-historia/(?P<id_proyecto>\d+)$', HistoriaUsuarioCrearView.as_view(), name='create-historia'),    
    url(r'^editar-historia/(?P<id_proyecto>\d+)/(?P<pk>\d+)$', HistoriaUsuarioEditarView.as_view(), name='edit-historia'),
    url(r'^eliminar-historia/(?P<id_proyecto>\d+)/(?P<pk>\d+)$', HistoriaUsuarioDeleteView.as_view(), name='delete-historia'),
    url(r'^detalle-historia/(?P<pk>\d+)$', HistoriaUsuarioDetailView.as_view(), name='detail-historia'),    
    url(r'^cargar-historias/(?P<id_proyecto>\d+)$', historiaUsuario_uploadfile, name='load-historias'),
    url(r'^dependencias-historias/(?P<pk>\d+)$', HistoriaDependenciaUdpateView.as_view(), name='dependencias-historias'),
    
]