from rest_framework import serializers
from django.utils import timezone
from .models import CategoriaProducto, Producto, HistorialPrecio


class CategoriaProductoSerializer(serializers.ModelSerializer):
    total_productos = serializers.SerializerMethodField()

    class Meta:
        model = CategoriaProducto
        fields = [
            "id",
            "nombre",
            "tipo",
            "descripcion",
            "activo",
            "fecha_creacion",
            "total_productos",
        ]
        read_only_fields = ["fecha_creacion", "total_productos"]

    def get_total_productos(self, obj):
        return obj.productos.filter(activo=True).count()


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de productos (optimizado)"""

    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True, allow_null=True)
    categoria_tipo = serializers.CharField(source="categoria.tipo", read_only=True, allow_null=True)
    estado_stock = serializers.CharField(read_only=True)
    necesita_reposicion = serializers.BooleanField(read_only=True)
    valor_inventario = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Producto
        fields = [
            "id",
            "codigo",
            "nombre",
            "categoria",
            "categoria_nombre",
            "categoria_tipo",
            "stock_actual",
            "stock_minimo",
            "stock_maximo",
            "unidad_medida",
            "precio_compra",
            "precio_venta",
            "estado",
            "estado_stock",
            "necesita_reposicion",
            "valor_inventario",
            "activo",
        ]


class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de producto"""

    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True, allow_null=True)
    categoria_tipo = serializers.CharField(source="categoria.tipo", read_only=True, allow_null=True)
    estado_stock = serializers.CharField(read_only=True)
    necesita_reposicion = serializers.BooleanField(read_only=True)
    valor_inventario = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    dias_vencimiento = serializers.IntegerField(read_only=True)
    proximo_vencimiento = serializers.CharField(read_only=True)
    proveedor_nombre = serializers.CharField(
        source="proveedor_principal.nombre", read_only=True, allow_null=True
    )
    creado_por_username = serializers.CharField(
        source="creado_por.username", read_only=True, allow_null=True
    )

    class Meta:
        model = Producto
        fields = "__all__"
        read_only_fields = [
            "fecha_creacion",
            "fecha_actualizacion",
            "estado_stock",
            "necesita_reposicion",
            "valor_inventario",
            "dias_vencimiento",
            "proximo_vencimiento",
        ]

    def validate_codigo(self, value):
        """Valida que el código sea único"""
        if self.instance and self.instance.codigo == value:
            return value

        if Producto.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Ya existe un producto con este código")
        return value

    def validate_stock_actual(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock actual no puede ser negativo")
        return value

    def validate_stock_minimo(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo")
        return value

    def validate_stock_maximo(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock máximo no puede ser negativo")
        return value

    def validate_precio_compra(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de compra debe ser mayor a 0")
        return value

    def validate_precio_venta(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de venta debe ser mayor a 0")
        return value

    def validate(self, data):
        # Validar que precio_venta > precio_compra
        precio_compra = data.get(
            "precio_compra", getattr(self.instance, "precio_compra", None)
        )
        precio_venta = data.get(
            "precio_venta", getattr(self.instance, "precio_venta", None)
        )

        if precio_venta and precio_compra and precio_venta <= precio_compra:
            raise serializers.ValidationError(
                {
                    "precio_venta": "El precio de venta debe ser mayor al precio de compra"
                }
            )

        stock_minimo = data.get(
            "stock_minimo", getattr(self.instance, "stock_minimo", None)
        )
        stock_maximo = data.get(
            "stock_maximo", getattr(self.instance, "stock_maximo", None)
        )

        if stock_maximo and stock_minimo and stock_maximo < stock_minimo:
            raise serializers.ValidationError(
                {"stock_maximo": "El stock máximo no puede ser menor al stock mínimo"}
            )

        fecha_vencimiento = data.get(
            "fecha_vencimiento", getattr(self.instance, "fecha_vencimiento", None)
        )
        if fecha_vencimiento and fecha_vencimiento < timezone.now().date():
            raise serializers.ValidationError(
                {
                    "fecha_vencimiento": "La fecha de vencimiento no puede ser en el pasado"
                }
            )

        return data

    def create(self, validated_data):
        # Solo agregar usuario si está autenticado
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["creado_por"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "precio_compra" in validated_data or "precio_venta" in validated_data:
            precio_compra_anterior = instance.precio_compra
            precio_venta_anterior = instance.precio_venta

            producto = super().update(instance, validated_data)

            if (
                precio_compra_anterior != producto.precio_compra
                or precio_venta_anterior != producto.precio_venta
            ):
                # Solo registrar historial si hay usuario autenticado
                request = self.context.get("request")
                historial_data = {
                    "producto": producto,
                    "precio_compra_anterior": precio_compra_anterior,
                    "precio_compra_nuevo": producto.precio_compra,
                    "precio_venta_anterior": precio_venta_anterior,
                    "precio_venta_nuevo": producto.precio_venta,
                }
                if request and request.user.is_authenticated:
                    historial_data["cambiado_por"] = request.user
                
                HistorialPrecio.objects.create(**historial_data)

            return producto

        return super().update(instance, validated_data)


class HistorialPrecioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    cambiado_por_username = serializers.CharField(
        source="cambiado_por.username", read_only=True, allow_null=True
    )

    class Meta:
        model = HistorialPrecio
        fields = "__all__"
