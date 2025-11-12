from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator

from .models import Habitaciones
from gestion_usuarios.views import role_required

from .models import Clientes
from .models import Reservas, Pagos
from django.utils import timezone
import uuid
from .forms import ReservaForm
from .models import ReservaHabitacion, ReservaServicio
from django.db import transaction


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista', 'gerente']), name='dispatch')
class HabitacionListView(LoginRequiredMixin, generic.ListView):
	model = Habitaciones
	template_name = 'habitaciones/list.html'
	context_object_name = 'habitaciones'


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class HabitacionCreateView(LoginRequiredMixin, generic.CreateView):
	model = Habitaciones
	fields = ['numero', 'piso', 'tipo', 'descripcion', 'precio_noche', 'capacidad', 'estado']
	template_name = 'habitaciones/form.html'
	success_url = reverse_lazy('habitaciones_list')


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class HabitacionUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Habitaciones
	fields = ['numero', 'piso', 'tipo', 'descripcion', 'precio_noche', 'capacidad', 'estado']
	template_name = 'habitaciones/form.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('habitaciones_list')


@method_decorator(role_required(allowed_roles=['administrador']), name='dispatch')
class HabitacionDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = Habitaciones
	template_name = 'habitaciones/confirm_delete.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('habitaciones_list')


def index(request):
	# Redirige al dashboard o a la lista de habitaciones según rol
	return render(request, 'dashboard.html')


# --- CRUD Clientes ---
@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class ClienteListView(LoginRequiredMixin, generic.ListView):
	model = Clientes
	template_name = 'clientes/list.html'
	context_object_name = 'clientes'


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class ClienteCreateView(LoginRequiredMixin, generic.CreateView):
	model = Clientes
	fields = ['rut', 'nombre', 'correo', 'telefono', 'direccion', 'activo']
	template_name = 'clientes/form.html'
	success_url = reverse_lazy('clientes_list')


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class ClienteUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Clientes
	fields = ['rut', 'nombre', 'correo', 'telefono', 'direccion', 'activo']
	template_name = 'clientes/form.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('clientes_list')


@method_decorator(role_required(allowed_roles=['administrador']), name='dispatch')
class ClienteDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = Clientes
	template_name = 'clientes/confirm_delete.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('clientes_list')


# --- CRUD Reservas ---
@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista', 'gerente']), name='dispatch')
class ReservasListView(LoginRequiredMixin, generic.ListView):
	model = Reservas
	template_name = 'reservas/list.html'
	context_object_name = 'reservas'


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class ReservasCreateView(LoginRequiredMixin, generic.CreateView):
	model = Reservas
	form_class = ReservaForm
	template_name = 'reservas/form.html'
	success_url = reverse_lazy('reservas_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		# Pasamos lista de RUTs para el datalist en la plantilla
		ctx['clientes_ruts'] = Clientes.objects.values_list('rut', flat=True)
		return ctx

	def _room_available(self, habitacion, start_date, end_date):
		# Revisa si la habitación está libre entre start_date (inclusive) y end_date (exclusive)
		overlapping = Reservas.objects.filter(
			reservahabitacion__id_habitacion=habitacion,
			fecha_checkin__lt=end_date,
			fecha_checkout__gt=start_date,
		).distinct()
		return not overlapping.exists()

	@transaction.atomic
	def form_valid(self, form):
		# Validaciones y asignación de habitaciones y servicios
		reserva = form.save(commit=False)
		reserva.id_usuario = self.request.user
		reserva.codigo_reserva = f'RES-{uuid.uuid4().hex[:8].upper()}'
		reserva.fecha_creacion = timezone.now()

		start = form.cleaned_data['fecha_checkin']
		end = form.cleaned_data['fecha_checkout']
		habitaciones = form.cleaned_data['habitaciones']
		servicios = form.cleaned_data.get('servicios')

		# Validar disponibilidad
		for h in habitaciones:
			if not self._room_available(h, start, end):
				form.add_error('habitaciones', f'La habitación {h.numero} no está disponible en esas fechas.')
				return self.form_invalid(form)

		# Guardar reserva
		reserva.save()

		total = 0
		nights = (end - start).days
		if nights <= 0:
			nights = 1

		# Crear relaciones ReservaHabitacion y sumar precios
		for h in habitaciones:
			ReservaHabitacion.objects.create(
				id_reserva=reserva,
				id_habitacion=h,
				precio_noche=h.precio_noche,
				estado_asignacion='activa'
			)
			total += (h.precio_noche or 0) * nights

		# Servicios
		if servicios:
			for s in servicios:
				# Cantidad por defecto 1
				ReservaServicio.objects.create(
					id_reserva=reserva,
					id_servicio=s,
					cantidad=1,
					precio_unitario=s.precio,
					total=s.precio
				)
				total += s.precio

		reserva.total_estimado = total
		reserva.save()

		return super().form_valid(form)


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class ReservasUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Reservas
	fields = ['id_cliente', 'fecha_checkin', 'fecha_checkout', 'cantidad_personas', 'estado', 'comentarios', 'total_estimado']
	template_name = 'reservas/form.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('reservas_list')


@method_decorator(role_required(allowed_roles=['administrador']), name='dispatch')
class ReservasDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = Reservas
	template_name = 'reservas/confirm_delete.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('reservas_list')


# --- CRUD Pagos ---
@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class PagosListView(LoginRequiredMixin, generic.ListView):
	model = Pagos
	template_name = 'pagos/list.html'
	context_object_name = 'pagos'


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class PagosCreateView(LoginRequiredMixin, generic.CreateView):
	model = Pagos
	# Usamos el nombre de campo nuevo 'detalles_adicionales' en lugar de 'referencia'
	fields = ['id_reserva', 'monto', 'metodo_pago', 'detalles_adicionales', 'estado_pago']
	template_name = 'pagos/form.html'
	success_url = reverse_lazy('pagos_list')

	def form_valid(self, form):
		pago = form.save(commit=False)
		pago.id_usuario = self.request.user
		pago.fecha_pago = timezone.now()
		pago.save()
		return super().form_valid(form)


@method_decorator(role_required(allowed_roles=['administrador', 'recepcionista']), name='dispatch')
class PagosUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Pagos
	fields = ['id_reserva', 'monto', 'metodo_pago', 'detalles_adicionales', 'estado_pago']
	template_name = 'pagos/form.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('pagos_list')


@method_decorator(role_required(allowed_roles=['administrador']), name='dispatch')
class PagosDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = Pagos
	template_name = 'pagos/confirm_delete.html'
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('pagos_list')
