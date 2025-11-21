from django.urls import path, include
from rest_framework import routers
from .views import ProveedorViewSet

router = routers.DefaultRouter()
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')

urlpatterns = [
    path('', include(router.urls)),
]
