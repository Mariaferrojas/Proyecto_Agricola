from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertaViewSet, ConfiguracionAlertaViewSet, HistorialAlertaViewSet

router = DefaultRouter()
router.register(r'alertas', AlertaViewSet, basename='alertas')
router.register(r'configuraciones', ConfiguracionAlertaViewSet, basename='configuraciones')
router.register(r'historial', HistorialAlertaViewSet, basename='historial')

urlpatterns = [
    path('', include(router.urls)),
]