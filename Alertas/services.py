from django.utils import timezone
from django.db import models
from datetime import timedelta
import logging
from .models import Alerta, ConfiguracionAlerta, HistorialAlerta
from Productos.models import Producto
from movimientos.models import Movimiento
from decimal import Decimal

logger = logging.getLogger(__name__)


class AlertaService:
    """Servicio para la gestión de alertas"""

    def crear_alerta_manual(
        self,
        tipo,
        nivel,
        titulo,
        mensaje,
        producto_id=None,
        proveedor_id=None,
        usuario=None,
        enviar_correo=False,
    ):
        """Crear una alerta manualmente"""
        alerta = Alerta(
            tipo=tipo,
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            creada_por=usuario,
            enviar_correo=enviar_correo,
            auto_generada=False,
        )

        if producto_id:
            try:
                alerta.producto = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                logger.warning(f"Producto con ID {producto_id} no encontrado")

        if proveedor_id:
            try:
                from proveedores.models import Proveedor

                alerta.proveedor = Proveedor.objects.get(id=proveedor_id)
            except Proveedor.DoesNotExist:
                logger.warning(f"Proveedor con ID {proveedor_id} no encontrado")

        alerta.save()

        # Enviar correo si está configurado
        if enviar_correo:
            self._enviar_correo_alerta(alerta)

        return alerta

    def ejecutar_revision_automatica(self):
        """Ejecutar revisión automática de alertas"""
        resultados = {"alertas_creadas": 0, "alertas_resueltas": 0, "errores": []}

        try:
            # Revisar stock crítico
            resultados["stock_critico"] = self._revisar_stock_critico()
            resultados["alertas_creadas"] += resultados["stock_critico"]["creadas"]

            # Revisar stock agotado
            resultados["stock_agotado"] = self._revisar_stock_agotado()
            resultados["alertas_creadas"] += resultados["stock_agotado"]["creadas"]

            # Revisar productos próximos a vencer
            resultados["proximos_vencer"] = self._revisar_proximos_vencer()
            resultados["alertas_creadas"] += resultados["proximos_vencer"]["creadas"]

            # Revisar productos vencidos
            resultados["productos_vencidos"] = self._revisar_productos_vencidos()
            resultados["alertas_creadas"] += resultados["productos_vencidos"]["creadas"]

            # Auto-resolver alertas
            resultados["auto_resueltas"] = self._auto_resolver_alertas()
            resultados["alertas_resueltas"] += resultados["auto_resueltas"]["resueltas"]

        except Exception as e:
            logger.error(f"Error en revisión automática: {str(e)}")
            resultados["errores"].append(str(e))

        return resultados

    def _revisar_stock_critico(self):
        """Revisar productos con stock crítico"""
        config = self._obtener_configuracion("STOCK_CRITICO")
        if not config or not config.activa:
            return {"creadas": 0, "existentes": 0}

        # Calcular umbral de stock crítico
        productos_criticos = Producto.objects.filter(
            activo=True, stock_actual__lte=models.F("stock_minimo"), stock_actual__gt=0
        )

        alertas_creadas = 0
        for producto in productos_criticos:
            # Verificar si ya existe una alerta activa para este producto
            alerta_existente = Alerta.objects.filter(
                producto=producto, tipo="STOCK_CRITICO", activa=True
            ).exists()

            if not alerta_existente or config.repetible:
                # Crear nueva alerta
                porcentaje_stock = (producto.stock_actual / producto.stock_minimo) * 100
                nivel = self._determinar_nivel_stock(porcentaje_stock, config)

                alerta = Alerta(
                    tipo="STOCK_CRITICO",
                    nivel=nivel,
                    titulo=f"Stock Crítico - {producto.nombre}",
                    mensaje=(
                        f"El producto {producto.nombre} ({producto.codigo}) tiene stock crítico. "
                        f"Stock actual: {producto.stock_actual} {producto.unidad_medida}. "
                        f"Stock mínimo: {producto.stock_minimo} {producto.unidad_medida}."
                    ),
                    producto=producto,
                    auto_generada=True,
                    enviar_correo=config.enviar_correo,
                    datos_adicionales={
                        "stock_actual": float(producto.stock_actual),
                        "stock_minimo": float(producto.stock_minimo),
                        "porcentaje_stock": float(porcentaje_stock),
                        "unidad_medida": producto.unidad_medida,
                    },
                )
                alerta.save()
                alertas_creadas += 1

                if config.enviar_correo:
                    self._enviar_correo_alerta(alerta)

        return {"creadas": alertas_creadas, "existentes": productos_criticos.count()}

    def _revisar_stock_agotado(self):
        """Revisar productos agotados"""
        config = self._obtener_configuracion("STOCK_AGOTADO")
        if not config or not config.activa:
            return {"creadas": 0, "existentes": 0}

        productos_agotados = Producto.objects.filter(activo=True, stock_actual__lte=0)

        alertas_creadas = 0
        for producto in productos_agotados:
            alerta_existente = Alerta.objects.filter(
                producto=producto, tipo="STOCK_AGOTADO", activa=True
            ).exists()

            if not alerta_existente or config.repetible:
                alerta = Alerta(
                    tipo="STOCK_AGOTADO",
                    nivel="URGENTE",
                    titulo=f"Stock Agotado - {producto.nombre}",
                    mensaje=(
                        f"El producto {producto.nombre} ({producto.codigo}) está agotado. "
                        f"Stock actual: {producto.stock_actual} {producto.unidad_medida}."
                    ),
                    producto=producto,
                    auto_generada=True,
                    enviar_correo=config.enviar_correo,
                    datos_adicionales={
                        "stock_actual": float(producto.stock_actual),
                        "unidad_medida": producto.unidad_medida,
                    },
                )
                alerta.save()
                alertas_creadas += 1

                if config.enviar_correo:
                    self._enviar_correo_alerta(alerta)

        return {"creadas": alertas_creadas, "existentes": productos_agotados.count()}

    def _revisar_proximos_vencer(self):
        """Revisar productos próximos a vencer"""
        config = self._obtener_configuracion("PROXIMO_VENCIMIENTO")
        if not config or not config.activa:
            return {"creadas": 0, "existentes": 0}

        fecha_limite = timezone.now().date() + timedelta(
            days=config.dias_aviso_vencimiento
        )
        productos_proximos_vencer = Producto.objects.filter(
            activo=True,
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date(),
        )

        alertas_creadas = 0
        for producto in productos_proximos_vencer:
            dias_restantes = (producto.fecha_vencimiento - timezone.now().date()).days
            alerta_existente = Alerta.objects.filter(
                producto=producto, tipo="PROXIMO_VENCIMIENTO", activa=True
            ).exists()

            if not alerta_existente or config.repetible:
                nivel = "ALTA" if dias_restantes <= 7 else "MEDIA"

                alerta = Alerta(
                    tipo="PROXIMO_VENCIMIENTO",
                    nivel=nivel,
                    titulo=f"Producto Próximo a Vencer - {producto.nombre}",
                    mensaje=(
                        f"El producto {producto.nombre} ({producto.codigo}) vence el "
                        f"{producto.fecha_vencimiento}. Quedan {dias_restantes} días."
                    ),
                    producto=producto,
                    auto_generada=True,
                    enviar_correo=config.enviar_correo,
                    datos_adicionales={
                        "fecha_vencimiento": producto.fecha_vencimiento.isoformat(),
                        "dias_restantes": dias_restantes,
                        "lote": producto.lote or "",
                    },
                )
                alerta.save()
                alertas_creadas += 1

                if config.enviar_correo:
                    self._enviar_correo_alerta(alerta)

        return {
            "creadas": alertas_creadas,
            "existentes": productos_proximos_vencer.count(),
        }

    def _revisar_productos_vencidos(self):
        """Revisar productos vencidos"""
        config = self._obtener_configuracion("PRODUCTO_VENCIDO")
        if not config or not config.activa:
            return {"creadas": 0, "existentes": 0}

        productos_vencidos = Producto.objects.filter(
            activo=True, fecha_vencimiento__lt=timezone.now().date()
        )

        alertas_creadas = 0
        for producto in productos_vencidos:
            alerta_existente = Alerta.objects.filter(
                producto=producto, tipo="PRODUCTO_VENCIDO", activa=True
            ).exists()

            if not alerta_existente or config.repetible:
                alerta = Alerta(
                    tipo="PRODUCTO_VENCIDO",
                    nivel="URGENTE",
                    titulo=f"Producto Vencido - {producto.nombre}",
                    mensaje=(
                        f"El producto {producto.nombre} ({producto.codigo}) está vencido desde "
                        f"{producto.fecha_vencimiento}. Se recomienda retirarlo del inventario."
                    ),
                    producto=producto,
                    auto_generada=True,
                    enviar_correo=config.enviar_correo,
                    datos_adicionales={
                        "fecha_vencimiento": producto.fecha_vencimiento.isoformat(),
                        "lote": producto.lote or "",
                    },
                )
                alerta.save()
                alertas_creadas += 1

                if config.enviar_correo:
                    self._enviar_correo_alerta(alerta)

        return {"creadas": alertas_creadas, "existentes": productos_vencidos.count()}

    def _auto_resolver_alertas(self):
        """Auto-resolver alertas cuando se cumplan las condiciones"""
        alertas_auto_resolubles = Alerta.objects.filter(
            activa=True,
            tipo__in=["STOCK_CRITICO", "STOCK_AGOTADO"],
            producto__isnull=False,
        )

        alertas_resueltas = 0
        for alerta in alertas_auto_resolubles:
            if alerta.puede_auto_resolver:
                alerta.marcar_como_atendida()
                alertas_resueltas += 1

                # Crear historial
                HistorialAlerta.objects.create(
                    alerta=alerta,
                    campo_modificado="estado",
                    valor_anterior=alerta.estado,
                    valor_nuevo="ATENDIDA",
                    modificado_por=None,  # Sistema
                )

        return {"resueltas": alertas_resueltas}

    def _obtener_configuracion(self, tipo_alerta):
        """Obtener configuración para un tipo de alerta"""
        try:
            return ConfiguracionAlerta.objects.get(tipo_alerta=tipo_alerta)
        except ConfiguracionAlerta.DoesNotExist:
            logger.warning(f"Configuración no encontrada para {tipo_alerta}")
            return None

    def _determinar_nivel_stock(self, porcentaje_stock, config):
        """Determinar nivel de alerta basado en porcentaje de stock"""
        if porcentaje_stock <= 10:
            return "URGENTE"
        elif porcentaje_stock <= float(config.porcentaje_stock_critico):
            return "ALTA"
        elif porcentaje_stock <= float(config.porcentaje_stock_critico) * float(Decimal('1.5')):
            return "MEDIA"
        else:
            return "BAJA"

    def _enviar_correo_alerta(self, alerta):
        """Enviar correo electrónico para una alerta"""
        # Esta es una implementación básica. Deberías integrar con tu servicio de email.
        try:
            # Aquí iría la lógica para enviar el correo
            # Por ejemplo, usando Django send_mail o un servicio como SendGrid
            logger.info(f"Enviando correo para alerta {alerta.id}")

            # Marcar como enviado
            alerta.correo_enviado = True
            alerta.fecha_envio_correo = timezone.now()
            alerta.save()

        except Exception as e:
            logger.error(f"Error enviando correo para alerta {alerta.id}: {str(e)}")
