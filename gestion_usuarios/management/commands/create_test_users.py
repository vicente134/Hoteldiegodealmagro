from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crea usuarios de prueba para todos los roles (administrador, recepcionista, gerente, mantenimiento)'

    def handle(self, *args, **options):
        from gestion_usuarios.models import Usuarios

        test_users = [
            {'nombre_usuario': 'admin_test', 'correo': 'admin@example.com', 'nombre_completo': 'Admin Test', 'password': 'adminpass', 'rol': 'administrador', 'is_staff': True, 'is_superuser': True},
            {'nombre_usuario': 'recep_test', 'correo': 'recep@example.com', 'nombre_completo': 'Recepcion Test', 'password': 'receppass', 'rol': 'recepcionista'},
            {'nombre_usuario': 'gerente_test', 'correo': 'gerente@example.com', 'nombre_completo': 'Gerente Test', 'password': 'gerentepass', 'rol': 'gerente'},
            {'nombre_usuario': 'mante_test', 'correo': 'mante@example.com', 'nombre_completo': 'Mantenimiento Test', 'password': 'mantepass', 'rol': 'mantenimiento'},
        ]

        created = 0
        for u in test_users:
            if Usuarios.objects.filter(nombre_usuario=u['nombre_usuario']).exists():
                self.stdout.write(self.style.WARNING(f"Usuario {u['nombre_usuario']} ya existe, se salta."))
                continue

            user = Usuarios(
                nombre_usuario=u['nombre_usuario'],
                correo=u['correo'],
                nombre_completo=u['nombre_completo'],
            )
            # Si se provee is_staff/is_superuser, asignarlos
            if u.get('is_staff'):
                user.is_staff = True
            if u.get('is_superuser'):
                user.is_superuser = True
            # Guardar la contraseña con el método del modelo
            user.set_password(u['password'])
            user.save()
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Usuario creado: {u['nombre_usuario']} (rol: {u['rol']})"))

        if created == 0:
            self.stdout.write(self.style.WARNING('No se crearon nuevos usuarios.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Se crearon {created} usuarios de prueba.'))
