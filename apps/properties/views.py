from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum, Q

from apps.users.permissions import IsAdminUser
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
    permission_classes = [IsAdminUser]  # Solo admins pueden gestionar propiedades
    def get_permissions(self):
        # Permitir acceso público solo si es un GET y rental_status=available
        if (
            self.action == 'list'
            and self.request.method == 'GET'
            and self.request.query_params.get('rental_status') == 'available'
        ):
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        """
        Filtrar propiedades por múltiples criterios:
        - use: tipo de uso de la propiedad (rental, personal, commercial)
        - rental_status: estado del rental (active/occupied, available, ending_soon) - puede ser múltiple
        - rental_type: tipo de rental (monthly, airbnb) - puede ser múltiple
        
        Ejemplos de URLs:
        - /api/properties/?use=rental
        - /api/properties/?rental_status=active
        - /api/properties/?rental_status=ending_soon
        - /api/properties/?rental_type=monthly
        - /api/properties/?use=rental&rental_status=active,available&rental_type=airbnb
        - /api/properties/?rental_status=ending_soon&rental_type=monthly
        """
        from apps.rentals.models import Rental
        from django.utils import timezone
        from datetime import timedelta
        
        queryset = Property.objects.filter(is_deleted__isnull=True)
        
        # Filtro por tipo de uso (rental, personal, commercial)
        use_type = self.request.query_params.get('use', None)
        if use_type:
            queryset = queryset.filter(use=use_type)
        
        # Filtro por rental_status (puede ser múltiple: "active", "available", "ending_soon")
        rental_status = self.request.query_params.get('rental_status', None)
        if rental_status:
            statuses = [s.strip() for s in rental_status.split(',')]
            
            # Verificar si incluye ending_soon
            has_ending_soon = 'ending_soon' in statuses
            
            # Mapear 'active' a 'occupied' (el valor real en la BD)
            mapped_statuses = []
            for status in statuses:
                if status == 'active' or status == 'occupied':
                    mapped_statuses.append('occupied')
                elif status != 'ending_soon':  # No agregar ending_soon a mapped_statuses
                    mapped_statuses.append(status)
            
            # Manejar ending_soon
            if has_ending_soon:
                today = timezone.now().date()
                ending_soon_date = today + timedelta(days=30)
                
                # Propiedades con rentals que terminan pronto (próximos 30 días)
                queryset = queryset.filter(
                    rentals__status='occupied',
                    rentals__check_out__gte=today,
                    rentals__check_out__lte=ending_soon_date
                ).distinct()
            elif 'available' in mapped_statuses and 'occupied' in mapped_statuses:
                # Si busca ambos, solo filtra por propiedades de rental
                queryset = queryset.filter(use='rental')
            elif 'occupied' in mapped_statuses:
                # Propiedades con rental activo (occupied)
                queryset = queryset.filter(rentals__status='occupied').distinct()
            elif 'available' in mapped_statuses:
                # Propiedades de rental sin rental activo o con rental available
                queryset = queryset.filter(use='rental').exclude(
                    rentals__status='occupied'
                ).distinct()
        
        # Filtro por rental_type (puede ser múltiple: "monthly" o "airbnb" o "monthly,airbnb")
        rental_type = self.request.query_params.get('rental_type', None)
        if rental_type:
            types = [t.strip() for t in rental_type.split(',')]
            
            # Propiedades que tienen al menos un rental del tipo especificado
            queryset = queryset.filter(rentals__rental_type__in=types).distinct()
        
        return queryset
    
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
            {'message': 'Property deleted successfully (soft delete)'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """
        GET /api/properties/choices/
        
        Get available options for choice fields
        
        Example:
        {
            "use": [
                {"value": "rental", "label": "Rental"},
                {"value": "Personal", "label": "Personal"},
                {"value": "Comercial", "label": "Commercial"}
            ],
            "type_building": [
                {"value": "Casa", "label": "House"},
                {"value": "Apartamento", "label": "Apartment"},
                {"value": "Oficina", "label": "Office"}
            ]
        }
        """
        return Response({
            'use': [{'value': code, 'label': label} for code, label in Property.USE_CHOICES],
            'type_building': [{'value': code, 'label': label} for code, label in Property.TYPE_BUILDINGS_CHOICES]
        })
    
    @action(detail=True, methods=['get'])
    def repairs_cost(self, request, pk=None):
        """
        GET /api/properties/{id}/repairs_cost/
        
        Get total cost of all repairs for this property
        
        Response:
        {
            "total_repairs": 1500000.00,
            "repairs_count": 5,
            "repairs": [...]
        }
        """
        property_instance = self.get_object()
        repairs = Repair.objects.filter(property=property_instance)
        total_cost = repairs.aggregate(total=Sum('cost'))['total'] or 0
        
        return Response({
            'total_repairs': total_cost,
            'repairs_count': repairs.count(),
            'repairs': RepairSerializer(repairs, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def financials(self, request, pk=None):
        """
        GET /api/properties/{id}/financials/
        
        Get complete financial summary for this property
        
        Response:
        {
            "income": {
                "rental_payments": 5000000.00,
                "total_income": 5000000.00
            },
            "expenses": {
                "obligations": 1200000.00,
                "repairs": 800000.00,
                "total_expenses": 2000000.00
            },
            "balance": 3000000.00
        }
        """
        from apps.finance.models import PropertyPayment
        from apps.rentals.models import RentalPayment
        
        property_instance = self.get_object()
        
        # INGRESOS - Pagos de rentals
        rental_payments = RentalPayment.objects.filter(
            rental__property=property_instance
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # GASTOS - Obligaciones pagadas
        obligation_payments = PropertyPayment.objects.filter(
            obligation__property=property_instance
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # GASTOS - Reparaciones
        repairs_cost = Repair.objects.filter(
            property=property_instance
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        total_income = rental_payments
        total_expenses = obligation_payments + repairs_cost
        balance = total_income - total_expenses
        
        return Response({
            'income': {
                'rental_payments': rental_payments,
                'total_income': total_income
            },
            'expenses': {
                'obligations': obligation_payments,
                'repairs': repairs_cost,
                'total_expenses': total_expenses
            },
            'balance': balance
        })
    
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Soft delete de una propiedad"""
        property = self.get_object()
        property.soft_delete()
        return Response({'status': 'Property deleted'})
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar una propiedad eliminada"""
        property = Property.objects.get(pk=pk)
        property.restore()
        return Response({'status': 'Property restored'})
    
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
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
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