from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='servicios_index'),
    path('list/', views.ServiciosListView.as_view(), name='servicios_list'),
    path('crear/', views.ServiciosCreateView.as_view(), name='servicios_create'),
    path('<int:pk>/editar/', views.ServiciosUpdateView.as_view(), name='servicios_update'),
    path('<int:pk>/eliminar/', views.ServiciosDeleteView.as_view(), name='servicios_delete'),
]
