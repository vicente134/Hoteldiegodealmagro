from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from gestion_usuarios.views import role_required
from gestion_reservas.models import Servicios


@role_required(allowed_roles=['administrador', 'gerente'])
def index(request):
    return render(request, 'servicios/index.html')


class ServiciosListView(LoginRequiredMixin, generic.ListView):
    model = Servicios
    template_name = 'servicios/list.html'
    context_object_name = 'servicios'


class ServiciosCreateView(LoginRequiredMixin, generic.CreateView):
    model = Servicios
    fields = ['nombre', 'descripcion', 'precio', 'activo']
    template_name = 'servicios/form.html'
    success_url = reverse_lazy('servicios_list')


class ServiciosUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Servicios
    fields = ['nombre', 'descripcion', 'precio', 'activo']
    template_name = 'servicios/form.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('servicios_list')


class ServiciosDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Servicios
    template_name = 'servicios/confirm_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('servicios_list')
from django.shortcuts import render

# Create your views here.
