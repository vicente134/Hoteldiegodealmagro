# gestion_usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La raíz del sitio (ej: http://localhost:8000/) será el Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Ejemplo de la ruta protegida por RBAC
    path('reportes/', views.vista_reportes_gerencia, name='reportes_gerencia'),
    
    # Administración de Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
]