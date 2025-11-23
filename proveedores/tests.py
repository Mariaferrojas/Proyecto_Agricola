from django.test import TestCase

# Basic tests placeholder for proveedores app

class ProveedorModelTest(TestCase):
    def test_str(self):
        from .models import Proveedor
        p = Proveedor(nombre='Test')
        self.assertEqual(str(p), 'Test')
