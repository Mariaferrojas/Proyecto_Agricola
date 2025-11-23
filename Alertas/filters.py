import django_filters
from django.db.models import Q, F
from .models import Alerta, ConfiguracionAlerta

class AlertaFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    fecha_creacion_range = django_filters.DateFromToRangeFilter(field_name='fecha_creacion')
    fecha_lectura_range = django_filters.DateFromToRangeFilter(field_name='fecha_lectura')
    fecha_atencion_range = django_filters.DateFromToRangeFilter(field_name='fecha_atencion')
    producto_codigo = django_filters.CharFilter(field_name='producto__codigo', lookup_expr='icontains')
    producto_nombre = django_filters.CharFilter(field_name='producto__nombre', lookup_expr='icontains')
    urgente = django_filters.BooleanFilter(method='filter_urgente')
    auto_resolubles = django_filters.BooleanFilter(method='filter_auto_resolubles')
    
    class Meta:
        model = Alerta
        fields = {
            'tipo': ['exact', 'in'],
            'nivel': ['exact', 'in'],
            'estado': ['exact', 'in'],
            'activa': ['exact'],
            'auto_generada': ['exact'],
            'producto': ['exact'],
            'proveedor': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos"""
        return queryset.filter(
            Q(titulo__icontains=value) |
            Q(mensaje__icontains=value) |
            Q(producto__nombre__icontains=value) |
            Q(producto__codigo__icontains=value)
        )
    
    def filter_urgente(self, queryset, name, value):
        """Filtrar alertas urgentes"""
        from django.utils import timezone
        from datetime import timedelta
        
        if value:
            return queryset.filter(
                Q(nivel='URGENTE') |
                Q(nivel='ALTA', fecha_creacion__lte=timezone.now()-timedelta(days=2))
            )
        return queryset
    
    def filter_auto_resolubles(self, queryset, name, value):
        """Filtrar alertas que pueden auto-resolverse"""
        if value:
            # Solo alertas de stock que pueden auto-resolverse
            return queryset.filter(
                tipo__in=['STOCK_CRITICO', 'STOCK_AGOTADO'],
                producto__isnull=False
            ).filter(
                Q(tipo='STOCK_CRITICO', producto__stock_actual__gt=F('producto__stock_minimo')) |
                Q(tipo='STOCK_AGOTADO', producto__stock_actual__gt=0)
            )
        return queryset

class ConfiguracionAlertaFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ConfiguracionAlerta
        fields = ['activa', 'auto_generar', 'enviar_correo']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(tipo_alerta__icontains=value)
        )