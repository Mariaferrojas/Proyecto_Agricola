from django.core.management.base import BaseCommand
from Alertas.services import AlertaService


class Command(BaseCommand):
    help = "Ejecuta la revisión automática de alertas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tipo",
            type=str,
            help="Tipo específico de alerta a revisar",
        )

    def handle(self, *args, **options):
        alerta_service = AlertaService()
        tipo = options.get("tipo")

        self.stdout.write("Iniciando revisión automática de alertas...")

        if tipo:
            self.stdout.write(f"Revisando alertas de tipo: {tipo}")
            # Lógica para revisar solo un tipo específico
        else:
            resultados = alerta_service.ejecutar_revision_automatica()

            self.stdout.write("Revisión completada:")
            self.stdout.write(f"  Alertas creadas: {resultados['alertas_creadas']}")
            self.stdout.write(f"  Alertas resueltas: {resultados['alertas_resueltas']}")

            if resultados["errores"]:
                self.stdout.write(self.style.ERROR("Errores encontrados:"))
                for error in resultados["errores"]:
                    self.stdout.write(f"  - {error}")
            else:
                self.stdout.write(self.style.SUCCESS("Revisión completada sin errores"))
