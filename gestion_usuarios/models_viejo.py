from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# --- Manager para que Django sepa crear usuarios con tu modelo ---
class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, correo, nombre_completo, contrasena=None, **extra_fields):
        if not correo:
            raise ValueError('El campo Correo es obligatorio')
        if not nombre_usuario:
            raise ValueError('El campo Nombre de Usuario es obligatorio')

        correo = self.normalize_email(correo)
        user = self.model(
            nombre_usuario=nombre_usuario,
            correo=correo,
            nombre_completo=nombre_completo,
            **extra_fields
        )
        user.set_password(contrasena)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, correo, nombre_completo, contrasena, **extra_fields):
        extra_fields.setdefault('rol', 'administrador') # Asigna el rol de admin por defecto
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Seteamos 'activo' a 1 (True)
        extra_fields.setdefault('activo', 1) 

        if extra_fields.get('rol') != 'administrador':
            raise ValueError('Superuser debe tener el rol de "administrador".')

        return self.create_user(nombre_usuario, correo, nombre_completo, contrasena, **extra_fields)

# --- Tu modelo 'Usuarios' adaptado ---
class Usuarios(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(unique=True, max_length=60)
    nombre_completo = models.CharField(max_length=120, blank=True, null=True)
    correo = models.CharField(unique=True, max_length=150, blank=True, null=True)
    contrasena = models.CharField(max_length=255) # Django usará esto para el hash
    
    # --- RBAC (Roles) ---
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('recepcionista', 'Recepcionista'),
        ('gerente', 'Gerente'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    # Usamos los 'choices' del SQL original, ya que max_length=13 coincide
    rol = models.CharField(max_length=13, choices=ROL_CHOICES, default='recepcionista')
    
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    # Convertimos el 'activo = models.IntegerField()' a un BooleanField
    activo = models.BooleanField(default=True) 
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Django maneja la fecha

    # --- Campos requeridos por Django Auth ---
    is_staff = models.BooleanField(default=False) # Permite acceso al Admin
    
    # Hacemos que 'is_active' de Django use tu campo 'activo'
    @property
    def is_active(self):
        return self.activo

    objects = UsuarioManager()

    # --- Campos para el login ---
    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo', 'nombre_completo'] # Campos pedidos al crear superusuario

    class Meta:
        db_table = 'usuarios' # Le dice a Django qué tabla usar
        # NO hay 'managed = False'

    def __str__(self):
        return self.nombre_usuario

    # --- Mapeamos 'password' y 'last_login' de Django a tus campos ---
    @property
    def password(self):
        return self.contrasena

    @password.setter
    def password(self, raw_password):
        self.set_password(raw_password)

    @property
    def last_login(self):
        return self.ultimo_acceso

    @last_login.setter
    def last_login(self, value):
        self.ultimo_acceso = value