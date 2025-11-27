from rest_framework import serializers
from .models import Proveedor
from Productos.models import Producto


class ProveedorSerializer(serializers.ModelSerializer):
    total_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'contacto', 'telefono', 'email', 'direccion', 'total_productos']
        read_only_fields = []
    
    def get_total_productos(self, obj):
        """Retorna el total de productos del proveedor"""
        # No existe una FK directa desde Producto a Proveedor; se usa el campo
        # `proveedor_principal` (texto) en `Producto`. Contamos productos cuyo
        # `proveedor_principal` coincide (case-insensitive) con el nombre del proveedor.
        return Producto.objects.filter(proveedor_principal__iexact=obj.nombre).count()

    def validate_email(self, value):
        """Valida el formato del email"""
        if value and '@' not in value:
            raise serializers.ValidationError("Email inválido")
        return value
    
    def validate_telefono(self, value):
        """Valida el teléfono"""
        if value and len(value) < 7:
            raise serializers.ValidationError("Teléfono debe tener al menos 7 dígitos")
        return value
