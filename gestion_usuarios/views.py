# gestion_usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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


# --- Ejemplo de una vista protegida por RBAC ---
# Solo 'gerente' y 'administrador' pueden entrar
@login_required # Primero logueado
@role_required(allowed_roles=['administrador', 'gerente']) # Luego revisa el rol
def vista_reportes_gerencia(request):
    # ... aquí iría la lógica para generar reportes ...
    return render(request, 'reportes.html') # (tendrías que crear este HTML)