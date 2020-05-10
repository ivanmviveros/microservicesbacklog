"""msbacklog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from historiasUsuario.views import index, home, landing, contactos
from django.conf.urls.static import static
from msbacklog.settings import base


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', index, name='index'),
    url(r'^$', landing, name='landing'),
    url(r'^home/$', home, name='home'),
    url(r'^contacto/$', contactos, name='contacto'),
    url(r'^historias/', include('historiasUsuario.urls', namespace='historias')),
    url(r'^microservicios/', include('microservicios.urls', namespace='microservicios')),
    url(r'^metricas/', include('metricas.urls', namespace='metricas')),
]

urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)