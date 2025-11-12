from django import forms
from .models import Reservas, Habitaciones, Servicios, Clientes
from django.utils import timezone


class FechaInput(forms.DateInput):
    input_type = 'date'


class ReservaForm(forms.ModelForm):
    habitaciones = forms.ModelMultipleChoiceField(
        queryset=Habitaciones.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text='Selecciona una o más habitaciones para la reserva.'
    )

    servicios = forms.ModelMultipleChoiceField(
        queryset=Servicios.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Selecciona servicios opcionales (si aplica).'
    )

    # Campo auxiliar para facilitar búsqueda por RUT
    rut_cliente = forms.CharField(required=False, max_length=20, help_text='Escribe el RUT del cliente para buscar.')

    class Meta:
        model = Reservas
        fields = ['id_cliente', 'fecha_checkin', 'fecha_checkout', 'cantidad_personas', 'comentarios', 'rut_cliente']
        widgets = {
            'fecha_checkin': FechaInput(),
            'fecha_checkout': FechaInput(),
        }

    def clean(self):
        cleaned = super().clean()
        checkin = cleaned.get('fecha_checkin')
        checkout = cleaned.get('fecha_checkout')

        # Si se proporcionó rut_cliente, asignar el id_cliente correspondiente
        rut = cleaned.get('rut_cliente')
        if rut and not cleaned.get('id_cliente'):
            try:
                cliente = Clientes.objects.get(rut=rut)
                cleaned['id_cliente'] = cliente
            except Clientes.DoesNotExist:
                raise forms.ValidationError(f'No se encontró cliente con RUT {rut}.')

        if checkin and checkout:
            if checkin >= checkout:
                raise forms.ValidationError('La fecha de check-in debe ser anterior a la de check-out.')
            if checkin < timezone.now().date():
                raise forms.ValidationError('La fecha de check-in no puede ser en el pasado.')

        return cleaned
