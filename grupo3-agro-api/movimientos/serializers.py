from rest_framework import serializers
from .models import Movimiento

class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = '__all__'

    def validate(self, data):
        if data['tipo'] == 'salida' and data['cantidad'] > getattr(data['producto'], 'stock_actual', 0):
            raise serializers.ValidationError("No hay suficiente stock")
        return data
