from django.test import TestCase

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CategoriaProducto, Producto

class ProductoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.categoria = CategoriaProducto.objects.create(
            nombre='Semillas Test',
            tipo='SEMILLA'
        )
    
    def test_crear_producto(self):
        """Test para crear un producto"""
        producto = Producto.objects.create(
            codigo='TEST001',
            nombre='Producto Test',
            categoria=self.categoria,
            stock_actual=100,
            stock_minimo=10,
            stock_maximo=1000,
            unidad_medida='KG',
            precio_compra=10.50,
            precio_venta=15.75,
            creado_por=self.user
        )
        
        self.assertEqual(producto.codigo, 'TEST001')
        self.assertEqual(producto.estado_stock, 'NORMAL')
        self.assertTrue(producto.necesita_reposicion is False)
    
    def test_stock_critico(self):
        """Test para producto con stock crítico"""
        producto = Producto.objects.create(
            codigo='TEST002',
            nombre='Producto Crítico',
            categoria=self.categoria,
            stock_actual=5,
            stock_minimo=10,
            unidad_medida='KG',
            precio_compra=10.50,
            precio_venta=15.75,
            creado_por=self.user
        )
        
        self.assertEqual(producto.estado_stock, 'CRITICO')
        self.assertTrue(producto.necesita_reposicion)

class ProductoAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.categoria = CategoriaProducto.objects.create(
            nombre='Semillas API',
            tipo='SEMILLA'
        )
    
    def test_listar_productos(self):
        """Test para listar productos"""
        url = '/api/productos/productos/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_crear_producto(self):
        """Test para crear producto via API"""
        url = '/api/productos/productos/'
        data = {
            'codigo': 'API001',
            'nombre': 'Producto API Test',
            'categoria': self.categoria.id,
            'stock_actual': 100,
            'stock_minimo': 10,
            'stock_maximo': 1000,
            'unidad_medida': 'KG',
            'precio_compra': '15.50',
            'precio_venta': '20.00',
            'descripcion': 'Producto de prueba para API'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(Producto.objects.get().codigo, 'API001')
    
    def test_stock_critico_endpoint(self):
        """Test para endpoint de stock crítico"""
        # Crear producto con stock crítico
        Producto.objects.create(
            codigo='CRITICO001',
            nombre='Producto Crítico',
            categoria=self.categoria,
            stock_actual=5,
            stock_minimo=10,
            unidad_medida='KG',
            precio_compra=10.50,
            precio_venta=15.75,
            creado_por=self.user
        )
        
        url = '/api/productos/productos/stock_critico/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_resumen_inventario(self):
        """Test para endpoint de resumen de inventario"""
        url = '/api/productos/productos/resumen_inventario/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('estadisticas_generales', response.data)
