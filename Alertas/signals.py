from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from .models import Alerta, HistorialAlerta
from Productos.models import Producto


@receiver(pre_save, sender=Alerta)
def track_alerta_changes(sender, instance, **kwargs):
    """Registrar cambios en las alertas"""
    if instance.pk:
        try:
            old_instance = Alerta.objects.get(pk=instance.pk)

            # Comparar campos importantes
            fields_to_track = ["estado", "nivel", "activa"]
            for field in fields_to_track:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)

                if old_value != new_value:
                    HistorialAlerta.objects.create(
                        alerta=instance,
                        campo_modificado=field,
                        valor_anterior=str(old_value),
                        valor_nuevo=str(new_value),
                        modificado_por=instance.atendida_por,  # O el usuario que hizo el cambio
                    )

        except Alerta.DoesNotExist:
            pass  # Es una nueva instancia


@receiver(post_save, sender=Producto)
def crear_alerta_stock_critico(sender, instance, created, **kwargs):
    """Crear alerta cuando un producto tenga stock crítico"""
    from .services import AlertaService

    if (
        not created
        and instance.stock_actual <= instance.stock_minimo
        and instance.stock_actual > 0
    ):
        alerta_service = AlertaService()

        # Verificar configuración
        config = alerta_service._obtener_configuracion("STOCK_CRITICO")
        if config and config.activa and config.auto_generar:
            # Verificar si ya existe una alerta activa
            alerta_existente = Alerta.objects.filter(
                producto=instance, tipo="STOCK_CRITICO", activa=True
            ).exists()

            if not alerta_existente or config.repetible:
                alerta_service._revisar_stock_critico()


@receiver(post_save, sender=Producto)
def crear_alerta_stock_agotado(sender, instance, created, **kwargs):
    """Crear alerta cuando un producto se agote"""
    from .services import AlertaService

    if not created and instance.stock_actual <= 0:
        alerta_service = AlertaService()

        config = alerta_service._obtener_configuracion("STOCK_AGOTADO")
        if config and config.activa and config.auto_generar:
            alerta_existente = Alerta.objects.filter(
                producto=instance, tipo="STOCK_AGOTADO", activa=True
            ).exists()

            if not alerta_existente or config.repetible:
                alerta_service._revisar_stock_agotado()
