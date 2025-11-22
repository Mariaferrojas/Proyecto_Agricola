from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, F, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta

from .models import CategoriaProducto, Producto, HistorialPrecio
from .serializers import (
    CategoriaProductoSerializer, 
    ProductoListSerializer, 
    ProductoDetailSerializer,
    HistorialPrecioSerializer
)
from .filters import ProductoFilter
from rest_framework.pagination import PageNumberPagination

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'activo']
    
    def get_queryset(self):
        queryset = CategoriaProducto.objects.all()
        
        # Filtro por búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Obtener productos de una categoría específica"""
        categoria = self.get_object()
        productos = categoria.productos.filter(activo=True)
        
        page = self.paginate_queryset(productos)
        if page is not None:
            serializer = ProductoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)

class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    class StandardResultsSetPagination(PageNumberPagination):
        page_size = 10

    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductoFilter
    
    def get_queryset(self):
        queryset = Producto.objects.select_related(
            'categoria', 'creado_por'
        ).prefetch_related('historial_precios')
        
        # Solo productos activos por defecto, a menos que se especifique lo contrario
        if self.request.query_params.get('incluir_inactivos') != 'true':
            queryset = queryset.filter(activo=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stock_critico(self, request):
        """Productos con stock crítico (stock_actual <= stock_minimo)"""
        productos_criticos = self.get_queryset().filter(
            stock_actual__lte=F('stock_minimo'),
            stock_actual__gt=0,
            activo=True
        )
        
        page = self.paginate_queryset(productos_criticos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(productos_criticos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stock_agotado(self, request):
        """Productos agotados (stock_actual = 0)"""
        productos_agotados = self.get_queryset().filter(
            stock_actual__lte=0,
            activo=True
        )
        
        page = self.paginate_queryset(productos_agotados)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(productos_agotados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos_vencer(self, request):
        """Productos próximos a vencer (30 días o menos)"""
        fecha_limite = datetime.now().date() + timedelta(days=30)
        productos_proximos_vencer = self.get_queryset().filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=datetime.now().date(),
            activo=True
        ).order_by('fecha_vencimiento')
        
        page = self.paginate_queryset(productos_proximos_vencer)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(productos_proximos_vencer, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumen_inventario(self, request):
        """Resumen general del inventario con estadísticas"""
        productos_activos = self.get_queryset().filter(activo=True)
        
        # Estadísticas básicas
        total_productos = productos_activos.count()
        productos_stock_critico = productos_activos.filter(
            stock_actual__lte=F('stock_minimo'),
            stock_actual__gt=0
        ).count()
        productos_agotados = productos_activos.filter(stock_actual__lte=0).count()
        productos_exceso = productos_activos.filter(
            stock_actual__gte=F('stock_maximo'),
            stock_maximo__gt=0
        ).count()
        
        # Valor total del inventario
        valor_total = productos_activos.aggregate(
            total=Sum(F('stock_actual') * F('precio_compra'))
        )['total'] or 0
        
        # Productos por categoría
        productos_por_categoria = productos_activos.values(
            'categoria__nombre', 'categoria__tipo'
        ).annotate(
            total=Count('id'),
            valor=Sum(F('stock_actual') * F('precio_compra'))
        ).order_by('-valor')
        
        # Productos que necesitan reposición urgente
        reposicion_urgente = productos_activos.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        
        data = {
            'estadisticas_generales': {
                'total_productos': total_productos,
                'productos_stock_critico': productos_stock_critico,
                'productos_agotados': productos_agotados,
                'productos_exceso_stock': productos_exceso,
                'productos_reposicion_urgente': reposicion_urgente,
                'valor_total_inventario': float(valor_total),
            },
            'distribucion_por_categoria': list(productos_por_categoria),
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def exportar_csv(self, request):
        """Exportar productos a CSV"""
        productos = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="productos_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Código', 'Nombre', 'Categoría', 'Stock Actual', 'Stock Mínimo', 
            'Stock Máximo', 'Unidad', 'Precio Compra', 'Precio Venta', 
            'Estado Stock', 'Valor Inventario', 'Ubicación', 'Activo'
        ])
        
        for producto in productos:
            writer.writerow([
                producto.codigo,
                producto.nombre,
                producto.categoria.nombre,
                float(producto.stock_actual),
                float(producto.stock_minimo),
                float(producto.stock_maximo),
                producto.get_unidad_medida_display(),
                float(producto.precio_compra),
                float(producto.precio_venta),
                producto.estado_stock,
                float(producto.valor_inventario),
                producto.ubicacion_almacen,
                'Sí' if producto.activo else 'No'
            ])
        
        return response
    
    @action(detail=True, methods=['get'])
    def historial_precios(self, request, pk=None):
        """Obtener historial de precios de un producto"""
        producto = self.get_object()
        historial = producto.historial_precios.all()
        
        page = self.paginate_queryset(historial)
        if page is not None:
            serializer = HistorialPrecioSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HistorialPrecioSerializer(historial, many=True)
        return Response(serializer.data)

class HistorialPrecioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialPrecio.objects.select_related('producto', 'cambiado_por')
    serializer_class = HistorialPrecioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['producto']
    
    def get_queryset(self):
        queryset = HistorialPrecio.objects.all()
        
    
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_cambio__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_cambio__date__lte=fecha_fin)
        
        return queryset.order_by('-fecha_cambio')