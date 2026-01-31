from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia
from .serializers import (
    PropertySerializer, PropertyDetailSerializer, PropertyLawSerializer, EnserSerializer, 
    EnserInventorySerializer, PropertyDetailsSerializer, PropertyMediaSerializer, 
    PropertyMediaListSerializer, PropertyMediaUploadSerializer, EnserInventoryCreateSerializer,
    EnserInventoryDetailSerializer, EnserCreateAndAddSerializer, PropertyLawCreateSerializer
)
from apps.maintenance.models import Repair
from apps.maintenance.serializers import RepairSerializer, RepairCreateSerializer

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
    
    @action(detail=True, methods=['get'])
    def laws(self, request, pk=None):
        """Listar todas las PropertyLaws de una propiedad"""
        property_instance = self.get_object()
        property_laws = property_instance.laws.all()
        serializer = PropertyLawSerializer(property_laws, many=True, context={'request': request})
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


class PropertyAddRepairView(generics.CreateAPIView):
    """Vista para añadir reparaciones a una propiedad específica"""
    serializer_class = RepairCreateSerializer
    
    def get_property(self):
        """Obtener la propiedad a partir del ID en la URL"""
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    
    def create(self, request, *args, **kwargs):
        """Crear una reparación asociada a la propiedad"""
        property_instance = self.get_property()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad
            repair = serializer.save(property=property_instance)
            # Devolver la respuesta con el serializer completo
            response_serializer = RepairSerializer(repair)
            return Response({
                'message': f'Reparación añadida exitosamente a {property_instance.name}',
                'repair': response_serializer.data
            }, status=status.HTTP_201_CREATED)


class PropertyAddEnserView(generics.CreateAPIView):
    """Vista para crear un nuevo enser y añadirlo al inventario de una propiedad específica"""
    serializer_class = EnserCreateAndAddSerializer
    
    def get_property(self):
        """Obtener la propiedad a partir del ID en la URL"""
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    
    def create(self, request, *args, **kwargs):
        """Crear un enser y añadirlo al inventario de la propiedad"""
        property_instance = self.get_property()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Crear el enser primero
            enser = Enser.objects.create(
                name=serializer.validated_data['name'],
                price=serializer.validated_data['price'],
                condition=serializer.validated_data['condition']
            )
            
            # Luego crear el registro de inventario asociando el enser a la propiedad
            inventory = EnserInventory.objects.create(
                property=property_instance,
                enser=enser,
                url_media=serializer.validated_data.get('url_media')
            )
            
            # Devolver la respuesta con el serializer completo
            response_serializer = EnserInventoryDetailSerializer(inventory)
            return Response({
                'message': f'Enser "{enser.name}" creado y añadido exitosamente al inventario de {property_instance.name}',
                'inventory': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyAddLawView(generics.CreateAPIView):
    """Vista para crear una ley/regulación asociada a una propiedad específica"""
    serializer_class = PropertyLawCreateSerializer
    
    def get_property(self):
        """Obtener la propiedad a partir del ID en la URL"""
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    
    def create(self, request, *args, **kwargs):
        """Crear un PropertyLaw asociado a la propiedad"""
        property_instance = self.get_property()
        
        # Debug: Imprimir qué archivos llegaron
        print("DEBUG - request.FILES:", request.FILES)
        print("DEBUG - request.data:", request.data)
        
        # Mapear el campo 'media' a 'url' si viene con ese nombre
        data = request.data.copy()
        if 'media' in request.FILES and 'url' not in request.FILES:
            data['url'] = request.FILES['media']
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad
            property_law = serializer.save(property=property_instance)
            
            # Debug: Verificar si el archivo se guardó
            print("DEBUG - property_law.url:", property_law.url)
            
            # Devolver la respuesta con el serializer completo y contexto
            response_serializer = PropertyLawSerializer(property_law, context={'request': request})
            return Response({
                'message': f'Ley/Regulación añadida exitosamente a {property_instance.name}',
                'property_law': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyLawDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para ver, editar o eliminar una PropertyLaw específica de una propiedad"""
    serializer_class = PropertyLawSerializer
    
    def get_queryset(self):
        """Filtrar PropertyLaws por la propiedad especificada"""
        property_id = self.kwargs.get('property_id')
        return PropertyLaw.objects.filter(property_id=property_id)
    
    def get_object(self):
        """Obtener la PropertyLaw específica"""
        law_id = self.kwargs.get('law_id')
        return get_object_or_404(self.get_queryset(), pk=law_id)
    
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle de una PropertyLaw"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Actualizar una PropertyLaw"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Mapear 'media' a 'url' si viene con ese nombre
        data = request.data.copy()
        if 'media' in request.FILES and 'url' not in request.FILES:
            data['url'] = request.FILES['media']
        
        serializer = PropertyLawCreateSerializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            response_serializer = PropertyLawSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar una PropertyLaw"""
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'PropertyLaw eliminada exitosamente'}, status=status.HTTP_204_NO_CONTENT)


class PropertyUploadMediaView(generics.CreateAPIView):
    """Vista para subir archivos a una propiedad específica"""
    serializer_class = PropertyMediaUploadSerializer
    
    def get_property(self):
        """Obtener la propiedad a partir del ID en la URL"""
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    
    def create(self, request, *args, **kwargs):
        """Subir archivos a la propiedad"""
        property_instance = self.get_property()
        
        # Obtener archivos del request.FILES (soporte para formularios HTML y FormData)
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
            'message': f'{len(created_media)} archivo(s) subido(s) exitosamente a {property_instance.name}',
            'media': created_media
        }, status=status.HTTP_201_CREATED)