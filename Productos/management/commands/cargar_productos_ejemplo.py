from django.core.management.base import BaseCommand
from Productos.models import CategoriaProducto, Producto

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para productos'
    
    def handle(self, *args, **options):
    
        categorias_data = [
            {'nombre': 'Maíz Híbrido', 'tipo': 'SEMILLA'},
            {'nombre': 'Frijol Negro', 'tipo': 'SEMILLA'},
            {'nombre': 'Fertilizante NPK', 'tipo': 'ABONO'},
            {'nombre': 'Herbicida Selectivo', 'tipo': 'HERBICIDA'},
            {'nombre': 'Palas Agrícolas', 'tipo': 'HERRAMIENTA'},
        ]
        
        for cat_data in categorias_data:
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Categoría creada: {categoria.nombre}')
        
   
        productos_data = [
            {
                'codigo': 'MAIZ-H001',
                'nombre': 'Maíz Híbrido Premium',
                'categoria': 'Maíz Híbrido',
                'stock_actual': 500,
                'stock_minimo': 100,
                'stock_maximo': 1000,
                'unidad_medida': 'KG',
                'precio_compra': 25.50,
                'precio_venta': 32.00,
            },
            {
                'codigo': 'FRIJOL-N001',
                'nombre': 'Frijol Negro Jamapa',
                'categoria': 'Frijol Negro',
                'stock_actual': 300,
                'stock_minimo': 50,
                'stock_maximo': 500,
                'unidad_medida': 'KG',
                'precio_compra': 18.75,
                'precio_venta': 24.00,
            },
            {
                'codigo': 'FERT-NPK',
                'nombre': 'Fertilizante NPK 17-17-17',
                'categoria': 'Fertilizante NPK',
                'stock_actual': 1000,
                'stock_minimo': 200,
                'stock_maximo': 2000,
                'unidad_medida': 'KG',
                'precio_compra': 12.80,
                'precio_venta': 16.50,
            },
        ]
        
        for prod_data in productos_data:
            categoria = CategoriaProducto.objects.get(nombre=prod_data.pop('categoria'))
            producto, created = Producto.objects.get_or_create(
                codigo=prod_data['codigo'],
                defaults={
                    **prod_data,
                    'categoria': categoria,
                    'descripcion': f'Producto de alta calidad - {prod_data["nombre"]}',
                }
            )
            if created:
                self.stdout.write(f'Producto creado: {producto.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS('Datos de ejemplo cargados exitosamente')
        )