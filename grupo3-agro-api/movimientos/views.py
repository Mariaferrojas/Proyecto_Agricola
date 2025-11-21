from django.shortcuts import render

from rest_framework import viewsets, filters
from .models import Movimiento
from .serializers import MovimientoSerializer
from django_filters.rest_framework import DjangoFilterBackend

class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'producto__nombre', 'fecha']
    ordering_fields = ['fecha', 'cantidad']
