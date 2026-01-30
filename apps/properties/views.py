from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia
from .serializers import (
    PropertySerializer, PropertyDetailSerializer, PropertyLawSerializer, EnserSerializer, 
    EnserInventorySerializer, PropertyDetailsSerializer, PropertyMediaSerializer, PropertyMediaListSerializer
)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_deleted__isnull=True)
    serializer_class = PropertySerializer
    
    def get_serializer_class(self):
        """Usar PropertyDetailSerializer para ver detalle, PropertySerializer para listar/crear"""
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertySerializer
    
    def destroy(self, request, *args, **kwargs):
        """Sobrescribir DELETE para hacer soft delete en lugar de borrado físico"""
        instance = self.get_object()
        instance.soft_delete()
        return Response(
            {'message': 'Propiedad eliminada exitosamente (soft delete)'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para los campos choices"""
        return Response({
            'use': [{'value': code, 'label': label} for code, label in Property.USE_CHOICES],
            'type_building': [{'value': code, 'label': label} for code, label in Property.TYPE_BUILDINGS_CHOICES]
        })
    
    @action(detail=True, methods=['post'])
    def upload_media(self, request, pk=None):
        """Subir archivos media para una propiedad"""
        property_instance = self.get_object()
        files = request.FILES.getlist('files')
        media_type = request.data.get('media_type', 'image')
        
        if not files:
            return Response(
                {'error': 'No se proporcionaron archivos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_media = []
        for file in files:
            media = PropertyMedia.objects.create(
                property=property_instance,
                media_type=media_type,
                url=file
            )
            created_media.append(PropertyMediaSerializer(media).data)
        
        return Response({
            'message': f'{len(created_media)} archivo(s) subido(s) exitosamente',
            'media': created_media
        }, status=status.HTTP_201_CREATED)
    
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
    
    def get_serializer_class(self):
        """Usar diferentes serializers para listar y crear"""
        if self.action in ['list', 'retrieve']:
            return PropertyMediaListSerializer
        return PropertyMediaSerializer
    
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

