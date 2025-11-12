from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='reservas_index'),
    path('habitaciones/', views.HabitacionListView.as_view(), name='habitaciones_list'),
    path('habitaciones/crear/', views.HabitacionCreateView.as_view(), name='habitaciones_create'),
    path('habitaciones/<int:pk>/editar/', views.HabitacionUpdateView.as_view(), name='habitaciones_update'),
    path('habitaciones/<int:pk>/eliminar/', views.HabitacionDeleteView.as_view(), name='habitaciones_delete'),
    # Rutas CRUD para clientes
    path('clientes/', views.ClienteListView.as_view(), name='clientes_list'),
    path('clientes/crear/', views.ClienteCreateView.as_view(), name='clientes_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='clientes_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='clientes_delete'),
    # Rutas CRUD para reservas
    path('reservas/', views.ReservasListView.as_view(), name='reservas_list'),
    path('reservas/crear/', views.ReservasCreateView.as_view(), name='reservas_create'),
    path('reservas/<int:pk>/editar/', views.ReservasUpdateView.as_view(), name='reservas_update'),
    path('reservas/<int:pk>/eliminar/', views.ReservasDeleteView.as_view(), name='reservas_delete'),
    # Rutas CRUD para pagos
    path('pagos/', views.PagosListView.as_view(), name='pagos_list'),
    path('pagos/crear/', views.PagosCreateView.as_view(), name='pagos_create'),
    path('pagos/<int:pk>/editar/', views.PagosUpdateView.as_view(), name='pagos_update'),
    path('pagos/<int:pk>/eliminar/', views.PagosDeleteView.as_view(), name='pagos_delete'),
]
