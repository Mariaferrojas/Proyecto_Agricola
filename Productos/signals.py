from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from .models import Producto

@receiver(pre_save, sender=Producto)
def actualizar_estado_producto(sender, instance, **kwargs):
    """Actualizar estado del producto basado en stock"""
    if instance.stock_actual <= 0:
        instance.estado = 'AGOTADO'
    elif instance.stock_actual > 0:
        instance.estado = 'DISPONIBLE'

@receiver(post_save, sender=Producto)
def crear_alerta_stock(sender, instance, created, **kwargs):
    """Crear alerta automática si el stock es crítico"""
    if instance.necesita_reposicion:
        try:
            from Alertas.models import Alerta, ConfiguracionAlerta

            # Solo crear alerta automática si la configuración permite autogeneración
            config = ConfiguracionAlerta.objects.filter(
                tipo_alerta='STOCK_CRITICO', activa=True, auto_generar=True
            ).first()

            if config:
                Alerta.objects.get_or_create(
                    producto=instance,
                    tipo='STOCK_CRITICO',
                    defaults={
                        'mensaje': f'Stock crítico para {instance.nombre}. Stock actual: {instance.stock_actual} {instance.unidad_medida}',
                        'nivel': 'ALTA',
                        'activa': True,
                        'auto_generada': True,
                    }
                )
        except ImportError:
            # Si Alertas no está disponible, ignorar para evitar romper la creación de productos
            pass