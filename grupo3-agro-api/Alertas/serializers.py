from rest_framework import serializers
from django.utils import timezone
from .models import Alerta, ConfiguracionAlerta, HistorialAlerta


class AlertaListSerializer(serializers.ModelSerializer):
    """Serializer para listado de alertas (optimizado)"""

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_codigo = serializers.CharField(source="producto.codigo", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    dias_pendiente = serializers.IntegerField(read_only=True)
    es_urgente = serializers.BooleanField(read_only=True)
    creada_por_username = serializers.CharField(
        source="creada_por.username", read_only=True
    )

    class Meta:
        model = Alerta
        fields = [
            "id",
            "tipo",
            "tipo_display",
            "nivel",
            "nivel_display",
            "estado",
            "estado_display",
            "titulo",
            "mensaje",
            "producto",
            "producto_nombre",
            "producto_codigo",
            "fecha_creacion",
            "dias_pendiente",
            "es_urgente",
            "activa",
            "auto_generada",
            "creada_por_username",
        ]


class AlertaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de alerta"""

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_codigo = serializers.CharField(source="producto.codigo", read_only=True)
    producto_stock_actual = serializers.DecimalField(
        source="producto.stock_actual", read_only=True, max_digits=10, decimal_places=2
    )
    producto_stock_minimo = serializers.DecimalField(
        source="producto.stock_minimo", read_only=True, max_digits=10, decimal_places=2
    )
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    dias_pendiente = serializers.IntegerField(read_only=True)
    es_urgente = serializers.BooleanField(read_only=True)
    puede_auto_resolver = serializers.BooleanField(read_only=True)
    creada_por_username = serializers.CharField(
        source="creada_por.username", read_only=True
    )
    leida_por_username = serializers.CharField(
        source="leida_por.username", read_only=True
    )
    atendida_por_username = serializers.CharField(
        source="atendida_por.username", read_only=True
    )

    class Meta:
        model = Alerta
        fields = "__all__"
        read_only_fields = [
            "fecha_creacion",
            "fecha_lectura",
            "fecha_atencion",
            "fecha_resolucion",
            "dias_pendiente",
            "es_urgente",
            "puede_auto_resolver",
            "creada_por",
            "leida_por",
            "atendida_por",
            "correo_enviado",
            "fecha_envio_correo",
        ]

    def validate(self, data):
        # Validar fechas coherentes
        if data.get("fecha_lectura") and data["fecha_lectura"] > timezone.now():
            raise serializers.ValidationError(
                {"fecha_lectura": "La fecha de lectura no puede ser en el futuro"}
            )

        if data.get("fecha_atencion") and data["fecha_atencion"] > timezone.now():
            raise serializers.ValidationError(
                {"fecha_atencion": "La fecha de atención no puede ser en el futuro"}
            )

        # Validar transiciones de estado
        instance = self.instance
        if instance:
            estado_actual = instance.estado
            nuevo_estado = data.get("estado", estado_actual)

            if estado_actual != nuevo_estado:
                transiciones_validas = {
                    "PENDIENTE": ["LEIDA", "ATENDIDA", "DESCARTADA"],
                    "LEIDA": ["ATENDIDA", "DESCARTADA", "PENDIENTE"],
                    "ATENDIDA": ["LEIDA", "PENDIENTE"],
                    "DESCARTADA": ["LEIDA", "PENDIENTE"],
                }

                if nuevo_estado not in transiciones_validas.get(estado_actual, []):
                    raise serializers.ValidationError(
                        {
                            "estado": f"Transición no válida de {estado_actual} a {nuevo_estado}"
                        }
                    )

        return data

    def update(self, instance, validated_data):
        # Trackear cambios de estado
        usuario = self.context["request"].user
        estado_anterior = instance.estado
        nuevo_estado = validated_data.get("estado", estado_anterior)

        alerta = super().update(instance, validated_data)

        # Si el estado cambió, actualizar fechas y usuarios correspondientes
        if estado_anterior != nuevo_estado:
            if nuevo_estado == "LEIDA" and not instance.fecha_lectura:
                alerta.fecha_lectura = timezone.now()
                alerta.leida_por = usuario
            elif nuevo_estado == "ATENDIDA" and not instance.fecha_atencion:
                alerta.fecha_atencion = timezone.now()
                alerta.atendida_por = usuario
                alerta.activa = False
            elif nuevo_estado == "DESCARTADA" and not instance.fecha_resolucion:
                alerta.fecha_resolucion = timezone.now()
                alerta.atendida_por = usuario
                alerta.activa = False
            elif nuevo_estado == "PENDIENTE":
                alerta.fecha_lectura = None
                alerta.fecha_atencion = None
                alerta.fecha_resolucion = None
                alerta.leida_por = None
                alerta.atendida_por = None
                alerta.activa = True

            alerta.save()

        return alerta


class ConfiguracionAlertaSerializer(serializers.ModelSerializer):
    tipo_alerta_display = serializers.CharField(
        source="get_tipo_alerta_display", read_only=True
    )
    actualizado_por_username = serializers.CharField(
        source="actualizado_por.username", read_only=True
    )

    class Meta:
        model = ConfiguracionAlerta
        fields = "__all__"
        read_only_fields = ["fecha_actualizacion", "actualizado_por"]

    def validate_correo_destinatarios(self, value):
        """Validar formato de emails"""
        if value:
            emails = [email.strip() for email in value.split(",")]
            for email in emails:
                if email and "@" not in email:
                    raise serializers.ValidationError(f"Email inválido: {email}")
        return value

    def update(self, instance, validated_data):
        validated_data["actualizado_por"] = self.context["request"].user
        return super().update(instance, validated_data)


class HistorialAlertaSerializer(serializers.ModelSerializer):
    modificado_por_username = serializers.CharField(
        source="modificado_por.username", read_only=True
    )

    class Meta:
        model = HistorialAlerta
        fields = "__all__"


class AlertaStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de alertas"""

    total_alertas = serializers.IntegerField()
    alertas_pendientes = serializers.IntegerField()
    alertas_leidas = serializers.IntegerField()
    alertas_atendidas = serializers.IntegerField()
    alertas_urgentes = serializers.IntegerField()

    # Por tipo
    por_tipo = serializers.DictField(child=serializers.IntegerField())

    # Por nivel
    por_nivel = serializers.DictField(child=serializers.IntegerField())

    # Tiempo promedio de resolución (en días)
    tiempo_promedio_resolucion = serializers.FloatField()

    # Alertas por mes (últimos 6 meses)
    alertas_ultimos_meses = serializers.DictField(child=serializers.IntegerField())


class CrearAlertaManualSerializer(serializers.Serializer):
    """Serializer para crear alertas manualmente"""

    tipo = serializers.ChoiceField(choices=Alerta.TIPO_ALERTA_CHOICES)
    nivel = serializers.ChoiceField(
        choices=Alerta.NIVEL_ALERTA_CHOICES, default="MEDIA"
    )
    titulo = serializers.CharField(max_length=200)
    mensaje = serializers.CharField()
    producto_id = serializers.IntegerField(required=False, allow_null=True)
    proveedor_id = serializers.IntegerField(required=False, allow_null=True)
    enviar_correo = serializers.BooleanField(default=False)

    def validate(self, data):
        producto_id = data.get("producto_id")
        proveedor_id = data.get("proveedor_id")

        if not producto_id and not proveedor_id:
            raise serializers.ValidationError(
                "Debe especificar al menos un producto o proveedor"
            )

        return data
