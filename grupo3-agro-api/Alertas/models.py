from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from Productos.models import Producto


class Alerta(models.Model):
    TIPO_ALERTA_CHOICES = [
        ("STOCK_CRITICO", "Stock Crítico"),
        ("STOCK_AGOTADO", "Stock Agotado"),
        ("PROXIMO_VENCIMIENTO", "Próximo a Vencer"),
        ("PRODUCTO_VENCIDO", "Producto Vencido"),
        ("STOCK_EXCESO", "Exceso de Stock"),
        ("PRECIO_CAMBIO", "Cambio de Precio"),
        ("PEDIDO_PENDIENTE", "Pedido Pendiente"),
        ("INVENTARIO_BAJO", "Inventario Bajo"),
        ("SIN_MOVIMIENTOS", "Sin Movimientos Recientes"),
    ]

    NIVEL_ALERTA_CHOICES = [
        ("BAJA", "Baja"),
        ("MEDIA", "Media"),
        ("ALTA", "Alta"),
        ("URGENTE", "Urgente"),
    ]

    ESTADO_ALERTA_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("LEIDA", "Leída"),
        ("ATENDIDA", "Atendida"),
        ("DESCARTADA", "Descartada"),
    ]

    # Relaciones
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="alertas",
        null=True,
        blank=True,
    )

    movimiento = models.ForeignKey(
        "movimientos.Movimiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas",
    )
    proveedor = models.ForeignKey(
        "proveedores.Proveedor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas",
    )

    # Información básica de la alerta
    tipo = models.CharField(max_length=50, choices=TIPO_ALERTA_CHOICES)
    nivel = models.CharField(
        max_length=20, choices=NIVEL_ALERTA_CHOICES, default="MEDIA"
    )
    estado = models.CharField(
        max_length=20, choices=ESTADO_ALERTA_CHOICES, default="PENDIENTE"
    )

    # Mensaje y detalles
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    datos_adicionales = models.JSONField(
        default=dict, blank=True
    )  # Para almacenar datos específicos

    # Fechas importantes
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    # Seguimiento
    creada_por = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="alertas_creadas",
    )
    leida_por = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas_leidas",
    )
    atendida_por = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas_atendidas",
    )

    # Configuración de la alerta
    activa = models.BooleanField(default=True)
    auto_generada = models.BooleanField(
        default=False
    )  # Si fue generada automáticamente por el sistema
    repetible = models.BooleanField(default=True)  # Si puede generarse múltiples veces

    # Notificaciones
    enviar_correo = models.BooleanField(default=False)
    correo_enviado = models.BooleanField(default=False)
    fecha_envio_correo = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["tipo"]),
            models.Index(fields=["nivel"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["activa"]),
            models.Index(fields=["fecha_creacion"]),
            models.Index(fields=["producto", "tipo", "activa"]),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo}"

    def marcar_como_leida(self, usuario=None):
        """Marca la alerta como leída"""
        if self.estado == "PENDIENTE":
            self.estado = "LEIDA"
            self.fecha_lectura = timezone.now()
            if usuario:
                self.leida_por = usuario
            self.save()

    def marcar_como_atendida(self, usuario=None):
        """Marca la alerta como atendida"""
        self.estado = "ATENDIDA"
        self.fecha_atencion = timezone.now()
        if usuario:
            self.atendida_por = usuario
        self.activa = False
        self.save()

    def descartar(self, usuario=None):
        """Descarta la alerta"""
        self.estado = "DESCARTADA"
        self.fecha_resolucion = timezone.now()
        self.activa = False
        if usuario:
            self.atendida_por = usuario
        self.save()

    def reactivar(self):
        """Reactivar una alerta"""
        self.estado = "PENDIENTE"
        self.activa = True
        self.fecha_lectura = None
        self.fecha_atencion = None
        self.fecha_resolucion = None
        self.leida_por = None
        self.atendida_por = None
        self.save()

    @property
    def dias_pendiente(self):
        """Calcula los días que la alerta ha estado pendiente"""
        if self.estado == "PENDIENTE":
            delta = timezone.now() - self.fecha_creacion
            return delta.days
        return 0

    @property
    def es_urgente(self):
        """Determina si la alerta es urgente basado en nivel y tiempo"""
        if self.nivel == "URGENTE":
            return True
        elif self.nivel == "ALTA" and self.dias_pendiente > 2:
            return True
        elif self.nivel == "MEDIA" and self.dias_pendiente > 7:
            return True
        return False

    @property
    def puede_auto_resolver(self):
        """Determina si la alerta puede resolverse automáticamente"""
        # Por ejemplo, si el stock se normaliza, la alerta de stock crítico puede auto-resolverse
        if self.tipo == "STOCK_CRITICO" and self.producto:
            return self.producto.stock_actual > self.producto.stock_minimo
        elif self.tipo == "STOCK_AGOTADO" and self.producto:
            return self.producto.stock_actual > 0
        return False


class ConfiguracionAlerta(models.Model):
    """Configuración para tipos específicos de alertas"""

    tipo_alerta = models.CharField(
        max_length=50, choices=Alerta.TIPO_ALERTA_CHOICES, unique=True
    )

    # Configuración de generación
    activa = models.BooleanField(default=True)
    auto_generar = models.BooleanField(default=True)
    nivel_predeterminado = models.CharField(
        max_length=20, choices=Alerta.NIVEL_ALERTA_CHOICES, default="MEDIA"
    )

    # Configuración de notificaciones
    enviar_correo = models.BooleanField(default=False)
    correo_destinatarios = models.TextField(
        blank=True, help_text="Emails separados por coma"
    )

    # Configuración específica por tipo
    dias_aviso_vencimiento = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Días de anticipación para alertas de vencimiento",
    )
    porcentaje_stock_critico = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Porcentaje sobre stock mínimo para considerar crítico",
    )

    # Frecuencia de revisión
    intervalo_revision_horas = models.PositiveIntegerField(
        default=24,
        validators=[MinValueValidator(1), MaxValueValidator(168)],  # Máximo 1 semana
        help_text="Horas entre revisiones automáticas",
    )

    fecha_actualizacion = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Configuración de Alerta"
        verbose_name_plural = "Configuraciones de Alertas"

    def __str__(self):
        return f"Configuración - {self.get_tipo_alerta_display()}"


class HistorialAlerta(models.Model):
    """Historial de cambios en alertas"""

    alerta = models.ForeignKey(
        Alerta, on_delete=models.CASCADE, related_name="historial"
    )

    campo_modificado = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)

    fecha_modificacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = "Historial de Alerta"
        verbose_name_plural = "Historial de Alertas"
        ordering = ["-fecha_modificacion"]

    def __str__(self):
        return f"Historial {self.alerta} - {self.campo_modificado}"


# Create your models here.
