import django_filters
from django.db.models import Q, F
from .models import Producto, CategoriaProducto

class ProductoFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    estado_stock = django_filters.CharFilter(method='filter_estado_stock')
    rango_precio_compra = django_filters.RangeFilter(field_name='precio_compra')
    rango_precio_venta = django_filters.RangeFilter(field_name='precio_venta')
    rango_stock = django_filters.RangeFilter(field_name='stock_actual')
    necesita_reposicion = django_filters.BooleanFilter(method='filter_necesita_reposicion')
    proximo_vencer = django_filters.BooleanFilter(method='filter_proximo_vencer')
    
    class Meta:
        model = Producto
        fields = {
            'codigo': ['exact', 'icontains'],
            'nombre': ['exact', 'icontains'],
            'categoria': ['exact'],
            'categoria__tipo': ['exact'],
            'unidad_medida': ['exact'],
            'estado': ['exact'],
            'activo': ['exact'],
            'proveedor_principal': ['exact'],
            'fecha_vencimiento': ['exact', 'gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos"""
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(categoria__nombre__icontains=value)
        )
    
    def filter_estado_stock(self, queryset, name, value):
        """Filtrar por estado de stock calculado"""
        if value == 'AGOTADO':
            return queryset.filter(stock_actual__lte=0)
        elif value == 'CRITICO':
            return queryset.filter(
                stock_actual__lte=F('stock_minimo'),
                stock_actual__gt=0
            )
        elif value == 'EXCESO':
            return queryset.filter(
                stock_actual__gte=F('stock_maximo'),
                stock_maximo__gt=0
            )
        elif value == 'NORMAL':
            return queryset.filter(
                stock_actual__gt=F('stock_minimo'),
                stock_actual__lt=F('stock_maximo')
            )
        return queryset
    
    def filter_necesita_reposicion(self, queryset, name, value):
        """Filtrar productos que necesitan reposición"""
        if value:
            return queryset.filter(stock_actual__lte=F('stock_minimo'))
        return queryset
    
    def filter_proximo_vencer(self, queryset, name, value):
        """Filtrar productos próximos a vencer (30 días)"""
        from datetime import date, timedelta
        if value:
            fecha_limite = date.today() + timedelta(days=30)
            return queryset.filter(
                fecha_vencimiento__lte=fecha_limite,
                fecha_vencimiento__gte=date.today()
            )
        return queryset

class CategoriaProductoFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = CategoriaProducto
        fields = ['tipo', 'activo']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )