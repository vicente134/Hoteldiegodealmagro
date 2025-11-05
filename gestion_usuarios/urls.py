# gestion_usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La raíz del sitio (ej: http://localhost:8000/) será el Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Ejemplo de la ruta protegida por RBAC
    path('reportes/', views.vista_reportes_gerencia, name='reportes_gerencia'),
]