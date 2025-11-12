from django.test import TestCase
from django.urls import reverse
from gestion_usuarios.models import Usuarios
from .models import Clientes, Habitaciones
from django.utils import timezone


class ReservaFlowTests(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = Usuarios.objects.create_user('testuser', 'test@example.com', 'Test User', contrasena='testpass')
        # Crear cliente y habitación
        self.cliente = Clientes.objects.create(rut='11111111-1', nombre='Cliente Test')
        self.habitacion = Habitaciones.objects.create(numero='101', tipo='simple', precio_noche=50000, capacidad=2, estado='disponible')

    def test_login_and_create_reserva(self):
        login = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login)

        checkin = (timezone.now().date() + timezone.timedelta(days=1)).isoformat()
        checkout = (timezone.now().date() + timezone.timedelta(days=3)).isoformat()

        data = {
            'id_cliente': self.cliente.pk,
            'fecha_checkin': checkin,
            'fecha_checkout': checkout,
            'cantidad_personas': 2,
            'habitaciones': [self.habitacion.pk],
        }

        resp = self.client.post(reverse('reservas_create'), data)
        # Después de crear, debe redirigir al listado
        self.assertEqual(resp.status_code, 302)
from django.test import TestCase

# Create your tests here.
