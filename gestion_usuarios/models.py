# gestion_usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password

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
        # Hasheamos la contraseña usando el método del modelo
        if contrasena:
            user.set_password(contrasena)
        user.save(using=self._db)
        return user

    # Esta función está corregida para usar 'password'
    def create_superuser(self, nombre_usuario, correo, nombre_completo, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'administrador') 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True) 
        extra_fields.setdefault('activo', 1) 

        if extra_fields.get('rol') != 'administrador':
            raise ValueError('Superuser debe tener el rol de "administrador".')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        # Le pasamos la variable 'password' (de Django) 
        # al parámetro 'contrasena' de nuestra función 'create_user'.
        return self.create_user(
            nombre_usuario, 
            correo, 
            nombre_completo, 
            contrasena=password,
            **extra_fields
        )

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
    rol = models.CharField(max_length=13, choices=ROL_CHOICES, default='recepcionista')
    
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    activo = models.BooleanField(default=True) 
    intentos_fallidos = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Django maneja la fecha

    # --- Campos requeridos por Django Auth ---
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False) 

    @property
    def is_active(self):
        return self.activo

    objects = UsuarioManager()

    # --- Campos para el login ---
    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo', 'nombre_completo'] 

    class Meta:
        db_table = 'usuarios' 

    def __str__(self):
        return self.nombre_usuario

    # --- Mapeamos 'password' y 'last_login' de Django a tus campos ---
    @property
    def password(self):
        return self.contrasena

    # Overriding set_password to ensure the hashed value is stored in 'contrasena'
    def set_password(self, raw_password):
        """
        Hashea la contraseña y la guarda en el campo 'contrasena'.
        Esto evita doble-hashing si Django llama a set_password desde su propio flujo.
        """
        self.contrasena = make_password(raw_password)

    @property
    def last_login(self):
        return self.ultimo_acceso

    @last_login.setter
    def last_login(self, value):
        self.ultimo_acceso = value