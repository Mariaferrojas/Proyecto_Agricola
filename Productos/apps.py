from django.apps import AppConfig

class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Productos'
    verbose_name = 'Gestión de Productos'
    
    def ready(self):
        import Productos.signals