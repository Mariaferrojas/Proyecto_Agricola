from django.shortcuts import render

from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from .models import Movimiento
from .serializers import MovimientoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from Productos.models import Producto

class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'producto__nombre', 'fecha']
    ordering_fields = ['fecha', 'cantidad']
    
    def perform_create(self, serializer):
        """Guarda el movimiento y actualiza el stock del producto"""
        movimiento = serializer.save()
        
        # Actualizar stock del producto
        producto = movimiento.producto
        if movimiento.tipo == 'entrada':
            producto.stock_actual += movimiento.cantidad
        elif movimiento.tipo == 'salida':
            if producto.stock_actual >= movimiento.cantidad:
                producto.stock_actual -= movimiento.cantidad
            else:
                raise ValueError(f"Stock insuficiente. Disponible: {producto.stock_actual}")
        
        producto.save()
        return movimiento
    
    def create(self, request, *args, **kwargs):
        """Maneja la creación con validación de errores"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error al crear movimiento: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
