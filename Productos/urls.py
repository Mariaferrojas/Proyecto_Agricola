from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaProductoViewSet, ProductoViewSet, HistorialPrecioViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'historial-precios', HistorialPrecioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]