from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Proveedor
from .serializers import ProveedorSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = []  # Sin autenticación requerida
    
    def perform_create(self, serializer):
        """Guarda el proveedor"""
        return serializer.save()
    
    def create(self, request, *args, **kwargs):
        """Maneja la creación con validación"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': f'Error al crear proveedor: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
