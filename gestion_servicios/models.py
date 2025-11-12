
"""
Esta app reusa el modelo `Servicios` que ya está definido en `gestion_reservas.models`.
Mantener un segundo modelo con el mismo `db_table` causa errores de migración/test.
Por eso este archivo queda intencionalmente vacío y la app expone vistas que importan
el modelo desde `gestion_reservas`.
"""

from django.db import models

# Create your models here.
