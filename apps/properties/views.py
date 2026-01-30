from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia
from .serializers import (
    PropertySerializer, PropertyLawSerializer, EnserSerializer, EnserInventorySerializer, PropertyDetailsSerializer, PropertyMediaSerializer
)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_deleted__isnull=True)
    serializer_class = PropertySerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para los campos choices"""
        return Response({
            'use': [{'value': code, 'label': label} for code, label in Property.USE_CHOICES],
            'type_building': [{'value': code, 'label': label} for code, label in Property.TYPE_BUILDINGS_CHOICES]
        })
    
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Soft delete de una propiedad"""
        property = self.get_object()
        property.soft_delete()
        return Response({'status': 'Propiedad eliminada'})
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar una propiedad eliminada"""
        property = Property.objects.get(pk=pk)
        property.restore()
        return Response({'status': 'Propiedad restaurada'})
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """Listar propiedades eliminadas"""
        deleted_properties = Property.objects.filter(is_deleted__isnull=False)
        serializer = self.get_serializer(deleted_properties, many=True)
        return Response(serializer.data)

class PropertyDetailsViewSet(viewsets.ModelViewSet):
    queryset = PropertyDetails.objects.all()
    serializer_class = PropertyDetailsSerializer

class PropertyMediaViewSet(viewsets.ModelViewSet):
    queryset = PropertyMedia.objects.all()
    serializer_class = PropertyMediaSerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para media_type"""
        return Response({
            'media_type': [{'value': code, 'label': label} for code, label in PropertyMedia.MEDIA_TYPE_CHOICES]
        })

class PropertyLawViewSet(viewsets.ModelViewSet):
    queryset = PropertyLaw.objects.all()
    serializer_class = PropertyLawSerializer

class EnserViewSet(viewsets.ModelViewSet):
    queryset = Enser.objects.all()
    serializer_class = EnserSerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para condition"""
        return Response({
            'condition': [{'value': code, 'label': label} for code, label in Enser.CONDITION_CHOICES]
        })

class EnserInventoryViewSet(viewsets.ModelViewSet):
    queryset = EnserInventory.objects.all()
    serializer_class = EnserInventorySerializer

