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
from django.contrib.auth import views as auth_views # Vistas de Login de Django

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Usamos las vistas de login y logout que Django ya trae
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True # Si ya está logueado, lo manda al dashboard
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login' # Cuando cierra sesión, lo manda al login
    ), name='logout'),
    
    # Incluimos las URLs de nuestra app de usuarios
    # La ruta vacía '' (homepage) será manejada por esta app
    path('', include('gestion_usuarios.urls')), 
]