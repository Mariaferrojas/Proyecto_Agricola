from django.contrib import admin
from django.utils.html import format_html
from .models import CategoriaProducto, Producto, HistorialPrecio

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'activo', 'total_productos', 'fecha_creacion']
    list_filter = ['tipo', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    
    def total_productos(self, obj):
        return obj.productos.count()
    total_productos.short_description = 'Total Productos'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'categoria', 'stock_actual', 'stock_minimo', 
        'estado_stock_colored', 'precio_compra', 'precio_venta', 'activo'
    ]
    list_filter = [
        'categoria__tipo', 'unidad_medida', 'estado', 'activo', 
        'fecha_creacion', 'fecha_vencimiento'
    ]
    search_fields = ['codigo', 'nombre', 'descripcion']
    list_editable = ['stock_minimo', 'activo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'estado_stock']
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'categoria', 'descripcion')
        }),
        ('Stock e Inventario', {
            'fields': (
                'stock_actual', 'stock_minimo', 'stock_maximo', 
                'unidad_medida', 'ubicacion_almacen'
            )
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta')
        }),
        ('Información Adicional', {
            'fields': (
                'proveedor_principal', 'lote', 'fecha_vencimiento',
                'estado', 'activo'
            )
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def estado_stock_colored(self, obj):
        color_map = {
            'AGOTADO': 'red',
            'CRITICO': 'orange',
            'NORMAL': 'green',
            'EXCESO': 'blue'
        }
        color = color_map.get(obj.estado_stock, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.estado_stock
        )
    estado_stock_colored.short_description = 'Estado Stock'
    
    def save_model(self, request, obj, form, change):
        if not obj.creado_por:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(HistorialPrecio)
class HistorialPrecioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'precio_compra_anterior', 'precio_compra_nuevo', 
                   'precio_venta_anterior', 'precio_venta_nuevo', 'fecha_cambio', 'cambiado_por']
    list_filter = ['fecha_cambio', 'cambiado_por']
    search_fields = ['producto__nombre', 'producto__codigo']
    readonly_fields = ['fecha_cambio']
    
    def has_add_permission(self, request):
        return False 
