"""
URL configuration for hotel_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# hotel_project/urls.py
from django.contrib import admin
from django.urls import path, include
from gestion_usuarios import views as usuarios_views
from django.contrib.auth import views as auth_views # Vistas de Login de Django

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ruta de login personalizada (usamos la vista de la app para mensajes)
    path('login/', usuarios_views.login_view, name='login'),

    # Logout usando la vista incorporada
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    # Incluimos las URLs de nuestra app de usuarios
    path('', include('gestion_usuarios.urls')),
    # Rutas para gestión de reservas (habitaciones, clientes, reservas)
    path('reservas/', include('gestion_reservas.urls')),
    path('servicios/', include('gestion_servicios.urls')),
]