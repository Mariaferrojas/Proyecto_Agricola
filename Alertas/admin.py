from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Alerta, ConfiguracionAlerta, HistorialAlerta


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "tipo",
        "nivel_colored",
        "estado",
        "titulo",
        "producto",
        "fecha_creacion",
        "activa",
        "auto_generada",
    ]
    list_filter = [
        "tipo",
        "nivel",
        "estado",
        "activa",
        "auto_generada",
        "fecha_creacion",
        "producto__categoria",
    ]
    search_fields = ["titulo", "mensaje", "producto__nombre", "producto__codigo"]
    readonly_fields = [
        "fecha_creacion",
        "fecha_lectura",
        "fecha_atencion",
        "fecha_resolucion",
        "creada_por",
        "leida_por",
        "atendida_por",
        "correo_enviado",
        "fecha_envio_correo",
    ]
    actions = ["marcar_como_leidas", "marcar_como_atendidas", "descartar_alertas"]

    fieldsets = (
        (
            "Información Básica",
            {"fields": ("tipo", "nivel", "estado", "titulo", "mensaje")},
        ),
        ("Relaciones", {"fields": ("producto", "movimiento", "proveedor")}),
        (
            "Configuración",
            {"fields": ("activa", "auto_generada", "repetible", "enviar_correo")},
        ),
        (
            "Fechas",
            {
                "fields": (
                    "fecha_creacion",
                    "fecha_lectura",
                    "fecha_atencion",
                    "fecha_resolucion",
                    "fecha_envio_correo",
                )
            },
        ),
        ("Usuarios", {"fields": ("creada_por", "leida_por", "atendida_por")}),
        ("Datos Adicionales", {"fields": ("datos_adicionales", "correo_enviado")}),
    )

    def nivel_colored(self, obj):
        color_map = {
            "URGENTE": "red",
            "ALTA": "orange",
            "MEDIA": "blue",
            "BAJA": "green",
        }
        color = color_map.get(obj.nivel, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_nivel_display(),
        )

    nivel_colored.short_description = "Nivel"

    def marcar_como_leidas(self, request, queryset):
        updated = queryset.update(estado="LEIDA", fecha_lectura=timezone.now())
        self.message_user(request, f"{updated} alertas marcadas como leídas.")

    marcar_como_leidas.short_description = "Marcar como leídas"

    def marcar_como_atendidas(self, request, queryset):
        updated = queryset.update(
            estado="ATENDIDA", fecha_atencion=timezone.now(), activa=False
        )
        self.message_user(request, f"{updated} alertas marcadas como atendidas.")

    marcar_como_atendidas.short_description = "Marcar como atendidas"

    def descartar_alertas(self, request, queryset):
        updated = queryset.update(
            estado="DESCARTADA", fecha_resolucion=timezone.now(), activa=False
        )
        self.message_user(request, f"{updated} alertas descartadas.")

    descartar_alertas.short_description = "Descartar alertas"


@admin.register(ConfiguracionAlerta)
class ConfiguracionAlertaAdmin(admin.ModelAdmin):
    list_display = [
        "tipo_alerta",
        "activa",
        "auto_generar",
        "nivel_predeterminado",
        "enviar_correo",
        "dias_aviso_vencimiento",
        "fecha_actualizacion",
    ]
    list_filter = ["activa", "auto_generar", "enviar_correo"]
    list_editable = ["activa", "auto_generar", "enviar_correo"]

    fieldsets = (
        (
            "Configuración General",
            {
                "fields": (
                    "tipo_alerta",
                    "activa",
                    "auto_generar",
                    "nivel_predeterminado",
                )
            },
        ),
        ("Notificaciones", {"fields": ("enviar_correo", "correo_destinatarios")}),
        (
            "Parámetros Específicos",
            {"fields": ("dias_aviso_vencimiento", "porcentaje_stock_critico")},
        ),
        ("Frecuencia", {"fields": ("intervalo_revision_horas",)}),
        ("Auditoría", {"fields": ("fecha_actualizacion", "actualizado_por")}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            obj.actualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(HistorialAlerta)
class HistorialAlertaAdmin(admin.ModelAdmin):
    list_display = [
        "alerta",
        "campo_modificado",
        "valor_anterior",
        "valor_nuevo",
        "fecha_modificacion",
    ]
    list_filter = ["campo_modificado", "fecha_modificacion", "modificado_por"]
    search_fields = ["alerta__titulo", "campo_modificado"]
    readonly_fields = ["fecha_modificacion"]

    def has_add_permission(self, request):
        return False  # No permitir agregar manualmente

    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar


# Register your models here.
