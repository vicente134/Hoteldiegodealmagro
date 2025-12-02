# gestion_usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse

# --- Este es el decorador para tu RBAC (Control de Acceso Basado en Roles) ---
# Revisa el campo 'rol' de tu modelo 'Usuarios'
def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # 1. Revisa si está logueado
            if not request.user.is_authenticated:
                return redirect('login') 
            
            # 2. Revisa si tiene el rol permitido
            if request.user.rol in allowed_roles:
                # Si tiene el rol, permite ver la vista
                return view_func(request, *args, **kwargs)
            else:
                # Si no tiene el rol, lo mandamos al dashboard
                # (o podríamos mandarlo a una página de 'permiso denegado')
                return redirect('dashboard')
        return wrapper_func
    return decorator


# --- Vista del Dashboard principal ---
# Solo usuarios logueados pueden entrar (gracias a @login_required)
@login_required
def dashboard_view(request):
    # request.user contiene el usuario logueado (de tu tabla 'usuarios')
    return render(request, 'dashboard.html')


def login_view(request):
    # Vista de login personalizada (opcional)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('dashboard'))
            else:
                messages.error(request, 'Usuario no activo.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html')

# gestion_usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from .models import Usuarios # Importar el modelo Usuarios al inicio

# --- Este es el decorador para tu RBAC (Control de Acceso Basado en Roles) ---
# Revisa el campo 'rol' de tu modelo 'Usuarios'
def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # 1. Revisa si está logueado
            if not request.user.is_authenticated:
                return redirect('login') 
            
            # 2. Revisa si tiene el rol permitido
            if request.user.rol in allowed_roles:
                # Si tiene el rol, permite ver la vista
                return view_func(request, *args, **kwargs)
            else:
                # Si no tiene el rol, lo mandamos al dashboard
                # (o podríamos mandarlo a una página de 'permiso denegado')
                return redirect('dashboard')
        return wrapper_func
    return decorator


# --- Vista del Dashboard principal ---
# Solo usuarios logueados pueden entrar (gracias a @login_required)
@login_required
def dashboard_view(request):
    # request.user contiene el usuario logueado (de tu tabla 'usuarios')
    return render(request, 'dashboard.html')


def login_view(request):
    # Vista de login personalizada (opcional)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Primero buscamos el usuario para gestionar intentos fallidos
        try:
            usuario_obj = Usuarios.objects.get(nombre_usuario=username)
        except Usuarios.DoesNotExist:
            usuario_obj = None

        if usuario_obj and not usuario_obj.activo:
             messages.error(request, 'Cuenta bloqueada o inactiva. Contacte al administrador.')
             return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Login exitoso, reseteamos contador
                user.intentos_fallidos = 0
                user.save()
                login(request, user)
                return redirect(reverse('dashboard'))
            else:
                messages.error(request, 'Usuario no activo.')
        else:
            # Login fallido
            if usuario_obj:
                usuario_obj.intentos_fallidos += 1
                if usuario_obj.intentos_fallidos >= 3:
                    usuario_obj.activo = False
                    usuario_obj.save()
                    messages.error(request, 'Cuenta bloqueada por múltiples intentos fallidos.')
                else:
                    usuario_obj.save()
                    messages.error(request, f'Usuario o contraseña incorrectos. Intentos restantes: {3 - usuario_obj.intentos_fallidos}')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                
    return render(request, 'login.html')


# --- Ejemplo de una vista protegida por RBAC ---
# Solo 'gerente' y 'administrador' pueden entrar
@login_required # Primero logueado
@role_required(allowed_roles=['administrador', 'gerente']) # Luego revisa el rol
def vista_reportes_gerencia(request):
    # ... aquí iría la lógica para generar reportes ...
    return render(request, 'reportes.html') # (tendrías que crear este HTML)

# --- Vistas de Administración de Usuarios ---

@login_required
@role_required(allowed_roles=['administrador'])
def lista_usuarios(request):
    # from .models import Usuarios # Importación local para evitar ciclos si los hubiera - Ya importado arriba
    usuarios = Usuarios.objects.all().order_by('-fecha_creacion')
    return render(request, 'gestion_usuarios/administrar_usuarios.html', {'usuarios': usuarios})

@login_required
@role_required(allowed_roles=['administrador'])
def editar_usuario(request, user_id):
    # from .models import Usuarios - Ya importado arriba
    # from django.shortcuts import get_object_or_404 - Ya importado arriba
    
    usuario_editar = get_object_or_404(Usuarios, id_usuario=user_id)
    
    if request.method == 'POST':
        # Actualizar datos
        nuevo_rol = request.POST.get('rol')
        nuevo_estado = request.POST.get('activo') == 'on' # Checkbox devuelve 'on' si está marcado
        
        # Validaciones básicas (opcional)
        if nuevo_rol in dict(Usuarios.ROL_CHOICES):
            usuario_editar.rol = nuevo_rol
        
        # Evitar que un admin se desactive a sí mismo por error (opcional pero recomendado)
        if usuario_editar.id_usuario == request.user.id_usuario and not nuevo_estado:
             messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
             usuario_editar.activo = nuevo_estado
             usuario_editar.save()
             messages.success(request, f'Usuario {usuario_editar.nombre_usuario} actualizado correctamente.')
             return redirect('lista_usuarios')

    return render(request, 'gestion_usuarios/editar_usuario.html', {'usuario': usuario_editar})

from .forms import UsuarioCreationForm

@login_required
@role_required(allowed_roles=['administrador'])
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            nuevo_usuario = form.save()
            messages.success(request, f'Usuario {nuevo_usuario.nombre_usuario} creado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioCreationForm()
    
    return render(request, 'gestion_usuarios/crear_usuario.html', {'form': form})
