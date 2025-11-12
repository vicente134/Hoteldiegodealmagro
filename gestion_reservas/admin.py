from django.contrib import admin
from .models import (
	Clientes, Habitaciones, Reservas, Pagos,
	ReservaHabitacion, Servicios, ReservaServicio, Auditoria
)


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
	list_display = ('id_cliente', 'rut', 'nombre', 'correo', 'telefono', 'activo')
	search_fields = ('rut', 'nombre', 'correo')


@admin.register(Habitaciones)
class HabitacionesAdmin(admin.ModelAdmin):
	list_display = ('id_habitacion', 'numero', 'tipo', 'precio_noche', 'capacidad', 'estado')
	search_fields = ('numero',)


@admin.register(Reservas)
class ReservasAdmin(admin.ModelAdmin):
	list_display = ('id_reserva', 'codigo_reserva', 'id_cliente', 'id_usuario', 'fecha_checkin', 'fecha_checkout', 'estado')
	search_fields = ('codigo_reserva',)


@admin.register(Pagos)
class PagosAdmin(admin.ModelAdmin):
	list_display = ('id_pago', 'id_reserva', 'fecha_pago', 'monto', 'metodo_pago', 'estado_pago')


@admin.register(ReservaHabitacion)
class ReservaHabitacionAdmin(admin.ModelAdmin):
	list_display = ('id_reserva_habitacion', 'id_reserva', 'id_habitacion', 'precio_noche', 'estado_asignacion')


@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
	list_display = ('id_servicio', 'nombre', 'precio', 'activo')


@admin.register(ReservaServicio)
class ReservaServicioAdmin(admin.ModelAdmin):
	list_display = ('id_reserva_servicio', 'id_reserva', 'id_servicio', 'cantidad', 'total')


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
	list_display = ('id_auditoria', 'tabla_afectada', 'id_registro', 'accion', 'usuario', 'fecha')
