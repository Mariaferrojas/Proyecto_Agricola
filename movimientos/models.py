from Productos.models import Producto
from django.db import models

TIPO_MOVIMIENTO = (('entrada', 'Entrada'), ('salida', 'Salida'))

class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"

class MovimientoExtra(models.Model):
    movimiento = models.OneToOneField(Movimiento, on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True)

