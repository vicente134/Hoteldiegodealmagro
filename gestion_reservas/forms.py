from django import forms
from .models import Reservas, Habitaciones, Servicios, Clientes
from django.utils import timezone


class FechaInput(forms.DateInput):
    input_type = 'date'


class ReservaForm(forms.ModelForm):
    habitaciones = forms.ModelMultipleChoiceField(
        queryset=Habitaciones.objects.filter(estado='lista'),
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
    rut_cliente = forms.CharField(
        required=False, 
        max_length=20, 
        help_text='Escribe el RUT del cliente para buscar.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'})
    )

    class Meta:
        model = Reservas
        fields = ['id_cliente', 'fecha_checkin', 'fecha_checkout', 'cantidad_personas', 'comentarios']
        widgets = {
            'fecha_checkin': FechaInput(attrs={'class': 'form-control'}),
            'fecha_checkout': FechaInput(attrs={'class': 'form-control'}),
            'cantidad_personas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'id_cliente': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'id_cliente': 'Cliente',
            'fecha_checkin': 'Fecha de Check-in',
            'fecha_checkout': 'Fecha de Check-out',
            'cantidad_personas': 'Cantidad de Personas',
            'comentarios': 'Comentarios',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que id_cliente no sea obligatorio si se proporciona rut_cliente
        self.fields['id_cliente'].required = False

    def clean(self):
        cleaned = super().clean()
        checkin = cleaned.get('fecha_checkin')
        checkout = cleaned.get('fecha_checkout')

        # Si se proporcionó rut_cliente, asignar el id_cliente correspondiente
        rut = cleaned.get('rut_cliente')
        if rut:
            rut = rut.strip()
            if rut:
                try:
                    cliente = Clientes.objects.get(rut=rut, activo=True)
                    cleaned['id_cliente'] = cliente
                except Clientes.DoesNotExist:
                    raise forms.ValidationError(f'No se encontró un cliente activo con RUT {rut}.')

        # Validar que se haya seleccionado o encontrado un cliente
        if not cleaned.get('id_cliente'):
            raise forms.ValidationError('Debes seleccionar un cliente o ingresar un RUT válido.')

        # Validar fechas
        if checkin and checkout:
            if checkin >= checkout:
                raise forms.ValidationError('La fecha de check-in debe ser anterior a la de check-out.')
            if checkin < timezone.now().date():
                raise forms.ValidationError('La fecha de check-in no puede ser en el pasado.')

        # Validar cantidad de personas
        cantidad = cleaned.get('cantidad_personas')
        if cantidad and cantidad < 1:
            raise forms.ValidationError('La cantidad de personas debe ser al menos 1.')

        return cleaned