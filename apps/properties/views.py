from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum, Q

from apps.users.permissions import IsAdminUser, IsAdminOrPublicReadOnly
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia
from .serializers import (
    PropertySerializer, PropertyDetailSerializer, PropertyLawSerializer, EnserSerializer, 
    EnserInventorySerializer, PropertyDetailsSerializer, PropertyMediaSerializer, 
    PropertyMediaListSerializer, PropertyMediaUploadSerializer, EnserInventoryCreateSerializer,
    EnserInventoryDetailSerializer, EnserCreateAndAddSerializer, PropertyLawCreateSerializer,
)
from apps.finance.serializers import PropertyPaymentSerializer, ObligationDetailSerializer
from apps.rentals.serializers import RentalPaymentSerializer
from apps.maintenance.models import Repair
from apps.maintenance.serializers import RepairSerializer, RepairCreateSerializer

'''
═══════════════════════════════════════════════════════════════════════════════════
🏠 PROPERTY VIEWSET - ENDPOINTS Y PERMISOS
═══════════════════════════════════════════════════════════════════════════════════

📋 LISTADO DE PROPIEDADES:
   GET /api/properties/
   
   🔓 PÚBLICO (sin autenticación):
      - GET /api/properties/?rental_status=available
        → Lista solo propiedades disponibles para alquilar (sin rentals activos)
        → No muestra información financiera
        → Incluye: ubicación, detalles, multimedia, enseres, reparaciones
   
   🔒 ADMIN (requiere autenticación):
      - GET /api/properties/
        → Lista TODAS las propiedades (sin filtros o con otros filtros)
      - GET /api/properties/?rental_status=occupied
        → Propiedades con rental activo (ocupadas)
      - GET /api/properties/?rental_status=ending_soon
        → Propiedades cuyo rental termina en los próximos 30 días
      - GET /api/properties/?use=rental
        → Filtrar por tipo de uso (rental, personal, commercial)
      - GET /api/properties/?rental_type=monthly,airbnb
        → Filtrar por tipo de rental

📄 DETALLE DE PROPIEDAD:
   GET /api/properties/{id}/
   
   🔓 PÚBLICO (sin autenticación):
      - Solo si la propiedad está disponible (available)
      - No muestra información financiera (repairs_cost, financials)
      - Incluye: detalles, ubicación, multimedia, enseres, reparaciones
   
   🔒 ADMIN (requiere autenticación):
      - Acceso completo a cualquier propiedad
      - Incluye toda la información financiera

⚙️ ACCIONES SOBRE PROPIEDADES:
   🔒 SOLO ADMIN (requiere autenticación):
      - POST /api/properties/ → Crear propiedad
      - PUT/PATCH /api/properties/{id}/ → Actualizar propiedad
      - DELETE /api/properties/{id}/ → Soft delete propiedad
      - POST /api/properties/{id}/soft_delete/ → Soft delete explícito
      - POST /api/properties/{id}/restore/ → Restaurar propiedad eliminada
      - GET /api/properties/deleted/ → Listar propiedades eliminadas

📊 INFORMACIÓN FINANCIERA:
   🔒 SOLO ADMIN (requiere autenticación):
      - GET /api/properties/{id}/repairs_cost/ → Total de reparaciones
      - GET /api/properties/{id}/financials/ → Resumen financiero completo

📚 OTRAS RUTAS:
   🔒 SOLO ADMIN:
      - GET /api/properties/choices/ → Opciones de campos choice
      - GET /api/properties/{id}/laws/ → Leyes/regulaciones de la propiedad

═══════════════════════════════════════════════════════════════════════════════════
📌 NOTA IMPORTANTE SOBRE ESTADOS:
═══════════════════════════════════════════════════════════════════════════════════

❌ NO USAR 'active' - Este campo ha sido eliminado
✅ USAR 'occupied' y 'available':

   - available: Propiedad de tipo 'rental' o 'commercial' SIN rentals activos
                → Puede mostrarse públicamente
                → Acepta nuevos rentals
   
   - occupied: Propiedad de tipo 'rental' o 'commercial' CON rental activo (status='occupied')
               → Solo admins pueden verla
               → NO acepta nuevos rentals hasta que el actual termine
   
   - ending_soon: Propiedad ocupada cuyo rental termina en los próximos 30 días
                  → Útil para planificar próximas disponibilidades

🗑️ SOFT DELETE:
   - Las propiedades con is_deleted != NULL están marcadas como eliminadas
   - NO aparecen en ninguna consulta (ni listados, ni conteos, ni estadísticas)
   - NO se consideran para cálculos financieros ni dashboard
   - Pueden restaurarse con POST /api/properties/{id}/restore/

═══════════════════════════════════════════════════════════════════════════════════
'''
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_deleted__isnull=True)
    serializer_class = PropertySerializer
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        """
        Permisos dinámicos:
        - Usuarios anónimos: pueden listar y ver detalles de propiedades disponibles
        - Admins: acceso completo a todo
        """
        # Permitir acceso público a propiedades disponibles (list y retrieve)
        if self.action in ['list', 'retrieve'] and self.request.method == 'GET':
            rental_status = self.request.query_params.get('rental_status')
            
            # Si solicita propiedades disponibles, es público
            if rental_status and 'available' in rental_status:
                return [AllowAny()]
            
            # Si es retrieve, verificar si la propiedad es available
            if self.action == 'retrieve':
                try:
                    property_id = self.kwargs.get('pk')
                    if property_id:
                        from apps.rentals.models import Rental
                        property_obj = Property.objects.get(pk=property_id, is_deleted__isnull=True)
                        # Verificar si la propiedad está disponible (sin rentals activos)
                        has_occupied_rental = Rental.objects.filter(
                            property=property_obj,
                            status='occupied'
                        ).exists()
                        if not has_occupied_rental and property_obj.use in ['rental', 'commercial']:
                            return [AllowAny()]
                except Property.DoesNotExist:
                    pass
        
        # Resto de acciones requieren admin
        return [IsAdminUser()]
    
    def get_queryset(self):
        """
        Filtrar propiedades por múltiples criterios:
        - use: tipo de uso de la propiedad (rental, personal, commercial)
        - rental_status: estado del rental (occupied, available, ending_soon) - puede ser múltiple
        - rental_type: tipo de rental (monthly, airbnb) - puede ser múltiple
        
        Ejemplos de URLs:
        - /api/properties/?use=rental
        - /api/properties/?rental_status=occupied → Propiedades con rental activo
        - /api/properties/?rental_status=available → Propiedades disponibles (PÚBLICO)
        - /api/properties/?rental_status=ending_soon → Rentals que terminan en 30 días
        - /api/properties/?rental_type=monthly
        - /api/properties/?use=rental&rental_status=occupied,available&rental_type=airbnb
        - /api/properties/?rental_status=ending_soon&rental_type=monthly
        
        ⚠️ IMPORTANTE: 'active' ya NO se usa, usar 'occupied' en su lugar
        """
        from apps.rentals.models import Rental
        from django.utils import timezone
        from datetime import timedelta
        
        queryset = Property.objects.filter(is_deleted__isnull=True)
        
        # Filtro por tipo de uso (rental, personal, commercial)
        use_type = self.request.query_params.get('use', None)
        if use_type:
            queryset = queryset.filter(use=use_type)
        
        # Filtro por rental_status (puede ser múltiple: "occupied", "available", "ending_soon")
        rental_status = self.request.query_params.get('rental_status', None)
        if rental_status:
            statuses = [s.strip() for s in rental_status.split(',')]
            
            # Verificar si incluye ending_soon
            has_ending_soon = 'ending_soon' in statuses
            
            # Procesar los estados solicitados
            # NOTA: 'occupied' es obsoleto, se mantiene compatibilidad mapéandolo a 'occupied'
            mapped_statuses = []
            for status in statuses:
                if status == 'occupied':  # Retrocompatibilidad
                    mapped_statuses.append('occupied')
                elif status == 'occupied':
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
                # Si busca ambos, solo filtra por propiedades de rental o commercial
                queryset = queryset.filter(use__in=['rental', 'commercial'])
            elif 'occupied' in mapped_statuses:
                # Propiedades con rental activo (occupied)
                queryset = queryset.filter(rentals__status='occupied').distinct()
            elif 'available' in mapped_statuses:
                # Propiedades de rental o commercial sin rental activo
                queryset = queryset.filter(use__in=['rental', 'commercial']).exclude(
                    rentals__status='occupied'
                ).distinct()
        
        # Filtro por rental_type (puede ser múltiple: "monthly" o "airbnb" o "monthly,airbnb")
        rental_type = self.request.query_params.get('rental_type', None)
        if rental_type:
            types = [t.strip() for t in rental_type.split(',')]
            
            # Filtrar por el campo rental_type de Property
            queryset = queryset.filter(rental_type__in=types)
        
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
    
    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def repairs_cost(self, request, pk=None):
        """
        🔒 SOLO ADMIN
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
    
    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def financials(self, request, pk=None):
        """
        🔒 SOLO ADMIN
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
        from apps.finance.models import PropertyPayment, Obligation
        from apps.rentals.models import RentalPayment
        
        property_instance = self.get_object()
        
        # INGRESOS - Pagos de rentals
        rental_payments = RentalPayment.objects.filter(
            rental__property=property_instance
        )
        rental_payments_total = rental_payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # GASTOS - Obligaciones pagadas
        obligation_payments = PropertyPayment.objects.filter(
            obligation__property=property_instance
        )
        obligation_payments_total = obligation_payments.aggregate(total=Sum('amount'))['total'] or 0
        
        obligations = Obligation.objects.filter(property=property_instance)
        
        # GASTOS - Reparaciones
        repairs_cost = Repair.objects.filter(
            property=property_instance
        )
        repairs_total= repairs_cost.aggregate(total=Sum('cost'))['total'] or 0
        
        total_income = rental_payments_total
        total_expenses = obligation_payments_total + repairs_total
        balance = total_income - total_expenses
        
        return Response({
             'income': {
                'total': total_income,
                'rental_payments': RentalPaymentSerializer(rental_payments, many=True).data,
            },
            'expenses': {
                'total': total_expenses,
                'obligation_payments': PropertyPaymentSerializer(obligation_payments, many=True).data,
                'repairs': RepairSerializer(repairs_cost, many=True).data,
            },
            'obligations': {
                'total': obligations.aggregate(total=Sum('amount'))['total'] or 0,
                'items': ObligationDetailSerializer(obligations, many=True).data,
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

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_main_image(self, request, pk=None):
        """Asignar como imagen principal una multimedia existente de la propiedad"""
        property_instance = self.get_object()
        media_id = request.data.get('media_id')

        if not media_id:
            return Response({
                'error': 'media_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        media = get_object_or_404(
            PropertyMedia,
            pk=media_id,
            property=property_instance
        )

        if media.media_type != 'image':
            return Response({
                'error': 'Only media_type=image can be set as main image'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Guardar la misma referencia del archivo de multimedia como imagen principal
        property_instance.image_url = media.url.name
        property_instance.save(update_fields=['image_url', 'updated_at'])

        image_url = property_instance.image_url.url if property_instance.image_url else None
        if image_url and request:
            image_url = request.build_absolute_uri(image_url)

        return Response({
            'message': 'Main image updated successfully',
            'property_id': property_instance.id,
            'media_id': media.id,
            'image_url': image_url
        }, status=status.HTTP_200_OK)

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
                'message': f'Enser "{enser.name}" created and added successfully to the inventory of {property_instance.name}',
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
        
        # Construir payload sin copiar request.data (evita errores con archivos temporales)
        allowed_fields = ['entity_name', 'legal_number', 'original_amount', 'is_paid']
        data = {}

        for field in allowed_fields:
            if field in request.data:
                value = request.data.get(field)
                # Normalizar strings vacios/null para campos opcionales
                if value in ['', 'null', 'None']:
                    value = None
                data[field] = value

        # Aceptar archivo en 'url' o en 'media' (compatibilidad frontend)
        if 'url' in request.FILES:
            data['url'] = request.FILES.get('url')
        elif 'media' in request.FILES:
            data['url'] = request.FILES.get('media')
        
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
        
        # Construir payload sin copiar request.data (evita errores con archivos temporales)
        allowed_fields = ['entity_name', 'legal_number', 'original_amount', 'is_paid']
        data = {}

        for field in allowed_fields:
            if field in request.data:
                value = request.data.get(field)
                # Normalizar strings vacios/null para campos opcionales
                if value in ['', 'null', 'None']:
                    value = None
                data[field] = value

        # Aceptar archivo en 'url' o en 'media' (compatibilidad frontend)
        if 'url' in request.FILES:
            data['url'] = request.FILES.get('url')
        elif 'media' in request.FILES:
            data['url'] = request.FILES.get('media')
        
        serializer = PropertyLawCreateSerializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            response_serializer = PropertyLawSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar una PropertyLaw"""
        instance = self.get_object()
        if instance.url:
            instance.url.delete(save=False)
        instance.delete()
        return Response({'message': 'PropertyLaw deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class PropertyMediaDetailView(generics.DestroyAPIView):
    """Vista para eliminar una multimedia específica de una propiedad"""
    serializer_class = PropertyMediaSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return PropertyMedia.objects.filter(property_id=property_id)

    def get_object(self):
        media_id = self.kwargs.get('media_id')
        return get_object_or_404(self.get_queryset(), pk=media_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Borrar primero el archivo físico y luego el registro en DB
        if instance.url:
            instance.url.delete(save=False)

        instance.delete()
        return Response({'message': 'Media deleted successfully'}, status=status.HTTP_200_OK)


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
                {'error': 'No files were provided'}, 
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
            'message': f'{len(created_media)} file(s) uploaded successfully to {property_instance.name}',
            'media': created_media
        }, status=status.HTTP_201_CREATED)