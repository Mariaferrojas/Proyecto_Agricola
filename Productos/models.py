from django.db import models
from django.core.validators import MinValueValidator

class CategoriaProducto(models.Model):
    TIPO_CHOICES = [
        ('SEMILLA', 'Semilla'),
        ('ABONO', 'Abono'),
        ('HERBICIDA', 'Herbicida'),
        ('HERRAMIENTA', 'Herramienta'),
        ('OTRO', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Producto(models.Model):
    UNIDAD_CHOICES = [
        ('KG', 'Kilogramos'),
        ('G', 'Gramos'),
        ('L', 'Litros'),
        ('ML', 'Mililitros'),
        ('UNIDAD', 'Unidades'),
        ('CAJA', 'Cajas'),
        ('BOLSA', 'Bolsas'),
    ]
    
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('AGOTADO', 'Agotado'),
        ('DESCONTINUADO', 'Descontinuado'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del producto")
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT, related_name='productos')
    descripcion = models.TextField(blank=True)
    
    # Información de stock
    stock_actual = models.DecimalField(
        max_digits=12, 
        decimal_places=3, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Stock actual en almacén"
    )
    stock_minimo = models.DecimalField(
        max_digits=12, 
        decimal_places=3, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Stock mínimo antes de generar alerta"
    )
    stock_maximo = models.DecimalField(
        max_digits=12, 
        decimal_places=3, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Capacidad máxima de almacenamiento"
    )
    
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_CHOICES)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Información adicional
    proveedor_principal = models.CharField(max_length=200, blank=True, help_text="Nombre del proveedor principal")
    ubicacion_almacen = models.CharField(max_length=100, blank=True, help_text="Ubicación en el almacén")
    lote = models.CharField(max_length=100, blank=True, help_text="Número de lote")
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
    # Estados
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='DISPONIBLE')
    activo = models.BooleanField(default=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='productos_creados'
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_vencimiento']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def estado_stock(self):
        """Calcula el estado del stock basado en niveles mínimos y máximos"""
        if self.stock_actual <= 0:
            return 'AGOTADO'
        elif self.stock_actual <= self.stock_minimo:
            return 'CRITICO'
        elif self.stock_actual >= self.stock_maximo and self.stock_maximo > 0:
            return 'EXCESO'
        else:
            return 'NORMAL'
    
    @property
    def necesita_reposicion(self):
        """Indica si el producto necesita reposición"""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def valor_inventario(self):
        """Calcula el valor total del producto en inventario"""
        return self.stock_actual * self.precio_compra
    
    @property
    def dias_vencimiento(self):
        """Calcula los días hasta el vencimiento"""
        if self.fecha_vencimiento:
            from datetime import date
            hoy = date.today()
            delta = self.fecha_vencimiento - hoy
            return delta.days
        return None
    
    @property
    def proximo_vencimiento(self):
        """Indica si el producto está próximo a vencer"""
        dias = self.dias_vencimiento
        if dias is not None:
            if dias <= 0:
                return 'VENCIDO'
            elif dias <= 30:
                return 'PROXIMO_VENCER'
        return 'NORMAL'

class HistorialPrecio(models.Model):
    """Modelo para trackear cambios de precio"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial_precios')
    precio_compra_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    precio_compra_nuevo = models.DecimalField(max_digits=12, decimal_places=2)
    precio_venta_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    precio_venta_nuevo = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    cambiado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Historial de Precio'
        verbose_name_plural = 'Historial de Precios'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"Cambio precio {self.producto} - {self.fecha_cambio}"