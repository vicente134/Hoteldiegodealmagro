from django.contrib import admin
from .models import Usuarios


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
	list_display = ('id_usuario', 'nombre_usuario', 'nombre_completo', 'correo', 'rol', 'activo')
	search_fields = ('nombre_usuario', 'correo', 'nombre_completo')
	list_filter = ('rol', 'activo')
	ordering = ('id_usuario',)
