from django.test import TestCase

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Alerta, ConfiguracionAlerta
from Productos.models import Producto, CategoriaProducto


class AlertaModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.categoria = CategoriaProducto.objects.create(
            nombre="Semillas Test", tipo="SEMILLA"
        )
        self.producto = Producto.objects.create(
            codigo="TEST001",
            nombre="Producto Test",
            categoria=self.categoria,
            stock_actual=5,
            stock_minimo=10,
            unidad_medida="KG",
            precio_compra=10.50,
            precio_venta=15.75,
            creado_por=self.user,
        )

    def test_crear_alerta(self):
        """Test para crear una alerta"""
        alerta = Alerta.objects.create(
            tipo="STOCK_CRITICO",
            nivel="ALTA",
            titulo="Stock Crítico Test",
            mensaje="El producto tiene stock crítico",
            producto=self.producto,
            creada_por=self.user,
        )

        self.assertEqual(alerta.tipo, "STOCK_CRITICO")
        self.assertEqual(alerta.nivel, "ALTA")
        self.assertEqual(alerta.estado, "PENDIENTE")
        self.assertTrue(alerta.activa)

    def test_marcar_como_leida(self):
        """Test para marcar alerta como leída"""
        alerta = Alerta.objects.create(
            tipo="STOCK_CRITICO",
            nivel="ALTA",
            titulo="Stock Crítico Test",
            mensaje="El producto tiene stock crítico",
            producto=self.producto,
            creada_por=self.user,
        )

        alerta.marcar_como_leida(self.user)

        self.assertEqual(alerta.estado, "LEIDA")
        self.assertIsNotNone(alerta.fecha_lectura)
        self.assertEqual(alerta.leida_por, self.user)

    def test_dias_pendiente(self):
        """Test para calcular días pendiente"""
        alerta = Alerta.objects.create(
            tipo="STOCK_CRITICO",
            nivel="ALTA",
            titulo="Stock Crítico Test",
            mensaje="El producto tiene stock crítico",
            producto=self.producto,
            creada_por=self.user,
        )

        # La alerta debería tener 0 días pendiente recién creada
        self.assertEqual(alerta.dias_pendiente, 0)


class AlertaAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.categoria = CategoriaProducto.objects.create(
            nombre="Semillas API", tipo="SEMILLA"
        )
        self.producto = Producto.objects.create(
            codigo="API001",
            nombre="Producto API Test",
            categoria=self.categoria,
            stock_actual=5,
            stock_minimo=10,
            unidad_medida="KG",
            precio_compra=10.50,
            precio_venta=15.75,
            creado_por=self.user,
        )

        self.alerta = Alerta.objects.create(
            tipo="STOCK_CRITICO",
            nivel="ALTA",
            titulo="Stock Crítico API Test",
            mensaje="El producto tiene stock crítico",
            producto=self.producto,
            creada_por=self.user,
        )

    def test_listar_alertas(self):
        """Test para listar alertas"""
        url = "/api/alertas/alertas/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_crear_alerta_manual(self):
        """Test para crear alerta manualmente via API"""
        url = "/api/alertas/alertas/crear_manual/"
        data = {
            "tipo": "STOCK_CRITICO",
            "nivel": "ALTA",
            "titulo": "Alerta Manual Test",
            "mensaje": "Esta es una alerta manual",
            "producto_id": self.producto.id,
            "enviar_correo": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alerta.objects.count(), 2)

    def test_marcar_alerta_leida(self):
        """Test para marcar alerta como leída via API"""
        url = f"/api/alertas/alertas/{self.alerta.id}/marcar_leida/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se actualizó en la base de datos
        self.alerta.refresh_from_db()
        self.assertEqual(self.alerta.estado, "LEIDA")
        self.assertIsNotNone(self.alerta.fecha_lectura)

    def test_resumen_alertas(self):
        """Test para endpoint de resumen de alertas"""
        url = "/api/alertas/alertas/resumen/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_alertas", response.data)
        self.assertIn("alertas_pendientes", response.data)


class AlertaServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.categoria = CategoriaProducto.objects.create(
            nombre="Semillas Service", tipo="SEMILLA"
        )

        # Producto con stock crítico
        self.producto_critico = Producto.objects.create(
            codigo="CRITICO001",
            nombre="Producto Crítico",
            categoria=self.categoria,
            stock_actual=5,
            stock_minimo=10,
            unidad_medida="KG",
            precio_compra=10.50,
            precio_venta=15.75,
            creado_por=self.user,
        )

        # Producto agotado
        self.producto_agotado = Producto.objects.create(
            codigo="AGOTADO001",
            nombre="Producto Agotado",
            categoria=self.categoria,
            stock_actual=0,
            stock_minimo=5,
            unidad_medida="KG",
            precio_compra=8.50,
            precio_venta=12.75,
            creado_por=self.user,
        )

        # Crear configuraciones
        ConfiguracionAlerta.objects.create(
            tipo_alerta="STOCK_CRITICO", activa=True, auto_generar=True
        )
        ConfiguracionAlerta.objects.create(
            tipo_alerta="STOCK_AGOTADO", activa=True, auto_generar=True
        )

    def test_revision_stock_critico(self):
        """Test para revisión automática de stock crítico"""
        from .services import AlertaService

        alerta_service = AlertaService()
        resultados = alerta_service._revisar_stock_critico()

        self.assertGreater(resultados["creadas"], 0)
        self.assertTrue(
            Alerta.objects.filter(
                producto=self.producto_critico, tipo="STOCK_CRITICO"
            ).exists()
        )

    def test_revision_stock_agotado(self):
        """Test para revisión automática de stock agotado"""
        from .services import AlertaService

        alerta_service = AlertaService()
        resultados = alerta_service._revisar_stock_agotado()

        self.assertGreater(resultados["creadas"], 0)
        self.assertTrue(
            Alerta.objects.filter(
                producto=self.producto_agotado, tipo="STOCK_AGOTADO"
            ).exists()
        )


# Create your tests here.
