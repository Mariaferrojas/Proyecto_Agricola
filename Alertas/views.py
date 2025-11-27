from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone
from datetime import timedelta
import json

from .models import Alerta, ConfiguracionAlerta, HistorialAlerta
from .serializers import (
    AlertaListSerializer,
    AlertaDetailSerializer,
    ConfiguracionAlertaSerializer,
    HistorialAlertaSerializer, 
    AlertaStatsSerializer,
    CrearAlertaManualSerializer,
)
from .filters import AlertaFilter
from .services import AlertaService
from rest_framework.pagination import PageNumberPagination


class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    permission_classes = []  # Sin autenticación requerida
    class StandardResultsSetPagination(PageNumberPagination):
        page_size = 10

    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AlertaFilter

    def get_queryset(self):
        queryset = Alerta.objects.select_related(
            "producto",
            "creada_por",
            "leida_por",
            "atendida_por",
            "proveedor",
            "movimiento",
        ).prefetch_related("historial")

        # Filtrar por alertas activas por defecto, a menos que se especifique lo contrario
        if self.request.query_params.get("incluir_inactivas") != "true":
            queryset = queryset.filter(activa=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AlertaListSerializer
        return AlertaDetailSerializer

    def perform_create(self, serializer):
        user = (
            self.request.user if getattr(self.request, "user", None) and self.request.user.is_authenticated else None
        )
        serializer.save(creada_por=user)

    @action(detail=True, methods=["post"])
    def marcar_leida(self, request, pk=None):
        """Marca una alerta como leída"""
        alerta = self.get_object()
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        alerta.marcar_como_leida(user)

        serializer = self.get_serializer(alerta)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def marcar_atendida(self, request, pk=None):
        """Marca una alerta como atendida"""
        alerta = self.get_object()
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        alerta.marcar_como_atendida(user)

        serializer = self.get_serializer(alerta)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def descartar(self, request, pk=None):
        """Descarta una alerta"""
        alerta = self.get_object()
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        alerta.descartar(user)

        serializer = self.get_serializer(alerta)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reactivar(self, request, pk=None):
        """Reactivar una alerta"""
        alerta = self.get_object()
        alerta.reactivar()

        serializer = self.get_serializer(alerta)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def resumen(self, request):
        """Resumen de estadísticas de alertas"""
        # Alertas por estado
        total_alertas = self.get_queryset().count()
        alertas_pendientes = self.get_queryset().filter(estado="PENDIENTE").count()
        alertas_leidas = self.get_queryset().filter(estado="LEIDA").count()
        alertas_atendidas = self.get_queryset().filter(estado="ATENDIDA").count()

        # Alertas urgentes (nivel URGENTE o ALTA con más de 2 días)
        alertas_urgentes = (
            self.get_queryset()
            .filter(
                Q(nivel="URGENTE")
                | Q(
                    nivel="ALTA", fecha_creacion__lte=timezone.now() - timedelta(days=2)
                )
            )
            .count()
        )

        # Alertas por tipo
        por_tipo = (
            self.get_queryset()
            .values("tipo")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        por_tipo_dict = {item["tipo"]: item["total"] for item in por_tipo}

        # Alertas por nivel
        por_nivel = (
            self.get_queryset()
            .values("nivel")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        por_nivel_dict = {item["nivel"]: item["total"] for item in por_nivel}

        # Tiempo promedio de resolución (solo alertas resueltas)
        tiempo_promedio = (
            self.get_queryset()
            .filter(fecha_resolucion__isnull=False)
            .annotate(
                tiempo_resolucion=ExpressionWrapper(
                    F("fecha_resolucion") - F("fecha_creacion"),
                    output_field=fields.DurationField(),
                )
            )
            .aggregate(promedio=Avg("tiempo_resolucion"))["promedio"]
        )

        tiempo_promedio_dias = (
            tiempo_promedio.total_seconds() / (24 * 3600) if tiempo_promedio else 0
        )

        # Alertas por mes (últimos 6 meses)
        seis_meses_atras = timezone.now() - timedelta(days=180)
        alertas_por_mes = (
            self.get_queryset()
            .filter(fecha_creacion__gte=seis_meses_atras)
            .annotate(mes=TruncMonth("fecha_creacion"))
            .values("mes")
            .annotate(total=Count("id"))
            .order_by("mes")
        )

        alertas_ultimos_meses = {
            item["mes"].strftime("%Y-%m"): item["total"] for item in alertas_por_mes
        }

        data = {
            "total_alertas": total_alertas,
            "alertas_pendientes": alertas_pendientes,
            "alertas_leidas": alertas_leidas,
            "alertas_atendidas": alertas_atendidas,
            "alertas_urgentes": alertas_urgentes,
            "por_tipo": por_tipo_dict,
            "por_nivel": por_nivel_dict,
            "tiempo_promedio_resolucion": round(tiempo_promedio_dias, 2),
            "alertas_ultimos_meses": alertas_ultimos_meses,
        }

        serializer = AlertaStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pendientes_urgentes(self, request):
        """Alertas pendientes y urgentes"""
        alertas_urgentes = (
            self.get_queryset()
            .filter(estado="PENDIENTE")
            .filter(
                Q(nivel="URGENTE")
                | Q(
                    nivel="ALTA", fecha_creacion__lte=timezone.now() - timedelta(days=2)
                )
            )
            .order_by("-nivel", "-fecha_creacion")
        )

        page = self.paginate_queryset(alertas_urgentes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(alertas_urgentes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def crear_manual(self, request):
        """Crear alerta manualmente"""
        serializer = CrearAlertaManualSerializer(data=request.data)
        if serializer.is_valid():
            # Usar el servicio para crear la alerta
            alerta_service = AlertaService()
            alerta = alerta_service.crear_alerta_manual(
                tipo=serializer.validated_data["tipo"],
                nivel=serializer.validated_data["nivel"],
                titulo=serializer.validated_data["titulo"],
                mensaje=serializer.validated_data["mensaje"],
                producto_id=serializer.validated_data.get("producto_id"),
                proveedor_id=serializer.validated_data.get("proveedor_id"),
                usuario=(request.user if getattr(request, "user", None) and request.user.is_authenticated else None),
                enviar_correo=serializer.validated_data.get("enviar_correo", False),
            )

            return Response(
                AlertaDetailSerializer(alerta).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def revisar_automaticas(self, request):
        """Ejecutar revisión automática de alertas"""
        alerta_service = AlertaService()
        resultados = alerta_service.ejecutar_revision_automatica()

        return Response(
            {"mensaje": "Revisión automática completada", "resultados": resultados}
        )

    @action(detail=False, methods=["post"])
    def limpiar_antiguas(self, request):
        """Limpiar alertas antiguas (más de 90 días)"""
        fecha_limite = timezone.now() - timedelta(days=90)
        alertas_eliminadas = (
            self.get_queryset()
            .filter(
                fecha_creacion__lte=fecha_limite, estado__in=["ATENDIDA", "DESCARTADA"]
            )
            .count()
        )

        self.get_queryset().filter(
            fecha_creacion__lte=fecha_limite, estado__in=["ATENDIDA", "DESCARTADA"]
        ).delete()

        return Response(
            {
                "mensaje": f"Se eliminaron {alertas_eliminadas} alertas antiguas",
                "alertas_eliminadas": alertas_eliminadas,
            }
        )


class ConfiguracionAlertaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionAlerta.objects.all()
    serializer_class = ConfiguracionAlertaSerializer
    permission_classes = []  # Sin autenticación requerida
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activa", "auto_generar"]

    def perform_update(self, serializer):
        user = (
            self.request.user if getattr(self.request, "user", None) and self.request.user.is_authenticated else None
        )
        serializer.save(actualizado_por=user)

    @action(detail=False, methods=["post"])
    def resetear_configuraciones(self, request):
        """Resetear configuraciones a valores por defecto"""
        configuraciones = ConfiguracionAlerta.objects.all()

        for config in configuraciones:
            config.activa = True
            config.auto_generar = True
            config.nivel_predeterminado = "MEDIA"
            config.enviar_correo = False
            config.correo_destinatarios = ""
            config.dias_aviso_vencimiento = 30
            config.porcentaje_stock_critico = 20.00
            config.intervalo_revision_horas = 24
            config.actualizado_por = (
                request.user if getattr(request, "user", None) and request.user.is_authenticated else None
            )
            config.save()

        return Response({"mensaje": "Configuraciones reseteadas a valores por defecto"})


class HistorialAlertaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialAlertaSerializer
    permission_classes = []  # Sin autenticación requerida
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["alerta", "modificado_por"]

    def get_queryset(self):
        return HistorialAlerta.objects.select_related(
            "alerta", "modificado_por"
        ).order_by("-fecha_modificacion")


# Create your views here.
