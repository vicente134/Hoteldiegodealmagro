from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gestion_reservas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habitaciones',
            name='tipo',
            field=models.CharField(choices=[('standart', 'Standart'), ('premium', 'Premium'), ('deluxe', 'Deluxe')], default='standart', max_length=20),
        ),
        migrations.AlterField(
            model_name='habitaciones',
            name='estado',
            field=models.CharField(choices=[('lista', 'Lista'), ('en preparacion', 'En preparación'), ('ocupada', 'Ocupada')], default='lista', max_length=20),
        ),
        migrations.AlterField(
            model_name='pagos',
            name='metodo_pago',
            field=models.CharField(choices=[('efectivo', 'Efectivo'), ('debito', 'Débito'), ('credito', 'Crédito'), ('transferencia', 'Transferencia')], default='efectivo', max_length=20),
        ),
    ]
