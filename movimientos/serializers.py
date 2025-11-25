from rest_framework import serializers
from .models import Movimiento
from Productos.models import Producto

class MovimientoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = Movimiento
        fields = ['id', 'producto', 'producto_nombre', 'tipo', 
                  'cantidad', 'fecha']
        read_only_fields = ['fecha']

    def validate_cantidad(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value

    def validate(self, data):
        """Validación adicional para movimientos de salida"""
        if data.get('tipo') == 'salida':
            producto = data.get('producto')
            cantidad = data.get('cantidad')
            
            if producto and cantidad:
                if producto.stock_actual < cantidad:
                    raise serializers.ValidationError({
                        'cantidad': f'Stock insuficiente. Disponible: {producto.stock_actual}'
                    })
        
        return data
