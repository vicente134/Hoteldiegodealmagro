# gestion_reservas/models.py
from django.db import models
# Importamos el modelo Usuarios desde la app gestion_usuarios
from gestion_usuarios.models import Usuarios 

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    rut = models.CharField(unique=True, max_length=20)
    nombre = models.CharField(max_length=120)
    correo = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True) # Django maneja la fecha
    activo = models.BooleanField(default=True) # Convertido de IntegerField

    def __str__(self):
        # Mostrar el RUT en las representaciones (evita 'Clientes object()' en selects)
        return self.rut

    class Meta:
        db_table = 'clientes'


class Habitaciones(models.Model):
    id_habitacion = models.AutoField(primary_key=True)
    numero = models.CharField(unique=True, max_length=20)
    piso = models.IntegerField(blank=True, null=True)
    # Tipos permitidos para la habitación
    TIPO_STANDART = 'standart'
    TIPO_PREMIUM = 'premium'
    TIPO_DELUXE = 'deluxe'
    TIPO_CHOICES = [
        (TIPO_STANDART, 'Standart'),
        (TIPO_PREMIUM, 'Premium'),
        (TIPO_DELUXE, 'Deluxe'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_STANDART)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    capacidad = models.IntegerField()
    # Estados de habitación
    ESTADO_LISTA = 'lista'
    ESTADO_PREPARACION = 'en preparacion'
    ESTADO_OCUPADA = 'ocupada'
    ESTADO_CHOICES = [
        (ESTADO_LISTA, 'Lista'),
        (ESTADO_PREPARACION, 'En preparación'),
        (ESTADO_OCUPADA, 'Ocupada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_LISTA)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Django maneja la fecha

    class Meta:
        db_table = 'habitaciones'

    def __str__(self):
        # Mostrar el número de habitación en selectores y representaciones
        return str(self.numero)


class Reservas(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    codigo_reserva = models.CharField(unique=True, max_length=30)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente')
    # Corregido: Apunta a 'Usuarios' importado
    id_usuario = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Django maneja la fecha
    fecha_checkin = models.DateField()
    fecha_checkout = models.DateField()
    cantidad_personas = models.IntegerField()
    estado = models.CharField(max_length=10)
    comentarios = models.TextField(blank=True, null=True)
    total_estimado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'reservas'

    def __str__(self):
        # Mostrar el código de reserva si existe, sino el id
        return self.codigo_reserva if self.codigo_reserva else str(self.id_reserva)


class Pagos(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_reserva = models.ForeignKey('Reservas', models.DO_NOTHING, db_column='id_reserva')
    fecha_pago = models.DateTimeField(auto_now_add=True) # Django maneja la fecha
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    # Métodos de pago permitidos
    METODO_EFECTIVO = 'efectivo'
    METODO_DEBITO = 'debito'
    METODO_CREDITO = 'credito'
    METODO_TRANSFERENCIA = 'transferencia'
    METODO_CHOICES = [
        (METODO_EFECTIVO, 'Efectivo'),
        (METODO_DEBITO, 'Débito'),
        (METODO_CREDITO, 'Crédito'),
        (METODO_TRANSFERENCIA, 'Transferencia'),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES, default=METODO_EFECTIVO)

    # Campo renombrado a 'detalles_adicionales' en el código, pero mantenemos la columna DB 'referencia'
    detalles_adicionales = models.CharField(db_column='referencia', max_length=200, blank=True, null=True)

    estado_pago = models.CharField(max_length=11)
    # Corregido: Apunta a 'Usuarios' importado
    id_usuario = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        db_table = 'pagos'


class ReservaHabitacion(models.Model):
    id_reserva_habitacion = models.AutoField(primary_key=True)
    id_reserva = models.ForeignKey('Reservas', models.DO_NOTHING, db_column='id_reserva')
    id_habitacion = models.ForeignKey(Habitaciones, models.DO_NOTHING, db_column='id_habitacion')
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_asignacion = models.DateTimeField(auto_now_add=True) # Django maneja la fecha
    estado_asignacion = models.CharField(max_length=8)

    class Meta:
        db_table = 'reserva_habitacion'
        unique_together = (('id_reserva', 'id_habitacion'),)


# Señales para actualizar el estado de las habitaciones cuando se registra un pago
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone as dj_timezone


@receiver(post_save, sender=Pagos)
def marcar_habitaciones_ocupadas(sender, instance, created, **kwargs):
    """
    Si el pago está en estado 'pagado' y la fecha actual está dentro del rango de la reserva,
    marca las habitaciones asociadas como 'ocupada'.
    """
    try:
        # Consideramos 'pagado' como el valor indicativo de pago efectivo
        if instance.estado_pago and instance.estado_pago.lower() == 'pagado':
            reserva = instance.id_reserva
            hoy = dj_timezone.now().date()
            if reserva.fecha_checkin <= hoy < reserva.fecha_checkout:
                asigns = ReservaHabitacion.objects.filter(id_reserva=reserva)
                for a in asigns:
                    h = a.id_habitacion
                    if h.estado != Habitaciones.ESTADO_OCUPADA:
                        h.estado = Habitaciones.ESTADO_OCUPADA
                        h.save()
    except Exception:
        # Evitar que un fallo en la señal rompa el flujo principal; en producción registrar el error
        pass


class Servicios(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True) # Convertido de IntegerField

    class Meta:
        db_table = 'servicios'


class ReservaServicio(models.Model):
    id_reserva_servicio = models.AutoField(primary_key=True)
    id_reserva = models.ForeignKey('Reservas', models.DO_NOTHING, db_column='id_reserva')
    id_servicio = models.ForeignKey('Servicios', models.DO_NOTHING, db_column='id_servicio')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'reserva_servicio'


class Auditoria(models.Model):
    id_auditoria = models.BigAutoField(primary_key=True)
    tabla_afectada = models.CharField(max_length=100, blank=True, null=True)
    id_registro = models.CharField(max_length=100, blank=True, null=True)
    accion = models.CharField(max_length=6)
    # Nota: 'usuario' es un CharField, no una ForeignKey, según tu 'inspectdb'. Lo dejamos tal cual.
    usuario = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True) # Django maneja la fecha
    detalles = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'auditoria'