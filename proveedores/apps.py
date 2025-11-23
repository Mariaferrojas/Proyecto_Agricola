from django.apps import AppConfig


class ProveedoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proveedores'
    verbose_name = 'Proveedores'

    def ready(self):
        # place for signals if needed later
        pass
