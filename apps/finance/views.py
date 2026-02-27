from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.users.permissions import IsAdminUser
from .models import ObligationType, Obligation, PaymentMethod, PropertyPayment, Notification
from .serializers import (
    ObligationTypeSerializer, 
    PaymentMethodSerializer,
    ObligationSerializer,
    ObligationDetailSerializer,
    ObligationCreateSerializer,
    PropertyPaymentSerializer,
    PropertyPaymentCreateSerializer,
    NotificationSerializer,
    NotificationCreateSerializer
)
from .filters import ObligationFilter, PropertyPaymentFilter, NotificationFilter
from .pagination import StandardPagination, LargePagination
from apps.properties.models import Property


# ========== VIEWSETS PARA CRUD COMPLETO ==========

class ObligationTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tipos de obligaciones
    - GET /api/obligation-types/ - Listar todos
    - POST /api/obligation-types/ - Crear nuevo
    - GET /api/obligation-types/{id}/ - Ver detalle
    - PUT/PATCH /api/obligation-types/{id}/ - Actualizar
    - DELETE /api/obligation-types/{id}/ - Eliminar
    - GET /api/obligation-types/choices/ - Obtener opciones disponibles (tax, seguro, cuota)
    """
    queryset = ObligationType.objects.all()
    serializer_class = ObligationTypeSerializer
    permission_classes = [IsAdminUser]  # Solo admins
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para crear tipos de obligaciones"""
        from .models import ObligationType
        return Response({
            'name': [
                {'value': code, 'label': label} 
                for code, label in ObligationType.OBLIGATION_TYPE_CHOICES
            ]
        })


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para métodos de pago
    - GET /api/payment-methods/ - Listar todos
    - POST /api/payment-methods/ - Crear nuevo
    - GET /api/payment-methods/{id}/ - Ver detalle
    - PUT/PATCH /api/payment-methods/{id}/ - Actualizar
    - DELETE /api/payment-methods/{id}/ - Eliminar
    - GET /api/payment-methods/choices/ - Obtener opciones disponibles
    """
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminUser]  # Solo admins
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para métodos de pago"""
        from .models import PaymentMethod
        return Response({
            'name': [
                {'value': code, 'label': label} 
                for code, label in PaymentMethod.PAYMENT_TYPES
            ]
        })


class ObligationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para todas las obligaciones del sistema con filtros y paginación
    
    ENDPOINTS:
    - GET /api/obligations/ - Listar todas (paginado)
    - GET /api/obligations/{id}/ - Ver detalle con pagos
    - PUT/PATCH /api/obligations/{id}/ - Actualizar
    - DELETE /api/obligations/{id}/ - Eliminar
    
    FILTROS DISPONIBLES:
    - ?temporality=monthly - Por temporalidad
    - ?obligation_type=1 - Por tipo de obligación
    - ?property=2 - Por propiedad
    - ?due_date_from=2026-02-01 - Fecha desde
    - ?due_date_to=2026-02-28 - Fecha hasta
    - ?amount_min=100000 - Monto mínimo
    - ?amount_max=500000 - Monto máximo
    - ?entity_contains=luz - Búsqueda en nombre
    
    BÚSQUEDA:
    - ?search=EAAB - Busca en entity_name y property__name
    
    ORDENAMIENTO:
    - ?ordering=due_date - Ordenar por fecha (ascendente)
    - ?ordering=-amount - Ordenar por monto (descendente)
    
    PAGINACIÓN:
    - ?page=1 - Página 1
    - ?page_size=50 - 50 resultados por página (max 100)
    
    EJEMPLO COMBINADO:
    GET /api/obligations/?property=2&due_date_from=2026-02-01&ordering=-amount&page=1
    """
    queryset = Obligation.objects.filter(property__is_deleted__isnull=True)
    permission_classes = [IsAdminUser]  # Solo admins
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ObligationFilter
    search_fields = ['entity_name', 'property__name']
    ordering_fields = ['due_date', 'amount', 'entity_name', 'created_at']
    ordering = ['-due_date']
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ObligationDetailSerializer
        return ObligationSerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Obtener las opciones disponibles para el campo temporality"""
        from .models import Obligation
        return Response({
            'temporality': [
                {'value': code, 'label': label} 
                for code, label in Obligation.TEMPORALITY_CHOICES
            ]
        })


# ========== VISTAS ANIDADAS PARA PROPERTIES ==========

class PropertyAddObligationView(generics.CreateAPIView):
    """
    Crear una obligación asociada a una propiedad
    POST /api/properties/{property_id}/add_obligation/
    
    Body:
    {
        "obligation_type": 1,
        "entity_name": "EAAB",
        "amount": 50000,
        "due_date": "2026-02-15",
        "temporality": "monthly"
    }
    """
    serializer_class = ObligationCreateSerializer
    
    def get_property(self):
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    
    def create(self, request, *args, **kwargs):
        property_instance = self.get_property()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad
            obligation = serializer.save(property=property_instance)
            # Devolver respuesta completa
            response_serializer = ObligationDetailSerializer(obligation, context={'request': request})
            return Response({
                'message': f'Obligation created successfully for {property_instance.name}',
                'obligation': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyObligationsListView(generics.ListAPIView):
    """
    Listar todas las obligaciones de una propiedad
    GET /api/properties/{property_id}/obligations/
    
    Retorna lista completa con pagos realizados y montos pendientes
    """
    serializer_class = ObligationDetailSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return Obligation.objects.filter(property_id=property_id)


class PropertyObligationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Ver, editar o eliminar una obligación específica de una propiedad
    GET /api/properties/{property_id}/obligations/{obligation_id}/
    PUT/PATCH /api/properties/{property_id}/obligations/{obligation_id}/
    DELETE /api/properties/{property_id}/obligations/{obligation_id}/
    """
    serializer_class = ObligationDetailSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return Obligation.objects.filter(property_id=property_id)
    
    def get_object(self):
        obligation_id = self.kwargs.get('obligation_id')
        return get_object_or_404(self.get_queryset(), pk=obligation_id)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = ObligationCreateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ObligationDetailSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'message': 'Obligation deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


# ========== VISTAS PARA PAGOS DE OBLIGACIONES ==========

class ObligationAddPaymentView(generics.CreateAPIView):
    """
    Añadir un pago a una obligación específica
    POST /api/properties/{property_id}/obligations/{obligation_id}/add_payment/
    
    Body:
    {
        "payment_method": 1,
        "amount": 50000,
        "date": "2026-02-01",
        "voucher_url": "https://..."  (opcional)
    }
    """
    serializer_class = PropertyPaymentCreateSerializer
    
    def get_obligation(self):
        property_id = self.kwargs.get('property_id')
        obligation_id = self.kwargs.get('obligation_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return get_object_or_404(
            Obligation, 
            pk=obligation_id, 
            property_id=property_id
        )
    
    def create(self, request, *args, **kwargs):
        obligation_instance = self.get_obligation()
        
        # Limpiar voucher_url si viene como string vacío
        data = request.data.copy()
        if 'voucher_url' in data and data['voucher_url'] == '':
            data.pop('voucher_url')
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # Validar que no se pague más de lo debido
            total_paid = sum(p.amount for p in obligation_instance.payments.all())
            new_amount = serializer.validated_data['amount']
            
            if total_paid + new_amount > obligation_instance.amount:
                return Response({
                    'error': f'Payment exceeds the obligation amount',
                    'obligation_amount': obligation_instance.amount,
                    'already_paid': total_paid,
                    'pending': obligation_instance.amount - total_paid,
                    'attempted': new_amount
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar el pago
            payment = serializer.save(obligation=obligation_instance)
            response_serializer = PropertyPaymentSerializer(payment, context={'request': request})
            
            # Calcular nuevo estado
            new_total_paid = total_paid + new_amount
            is_fully_paid = new_total_paid >= obligation_instance.amount
            
            return Response({
                'message': 'Payment registered successfully',
                'payment': response_serializer.data,
                'obligation_status': {
                    'total_amount': obligation_instance.amount,
                    'total_paid': new_total_paid,
                    'pending': obligation_instance.amount - new_total_paid,
                    'is_fully_paid': is_fully_paid
                }
            }, status=status.HTTP_201_CREATED)
        
        # Imprimir errores para debugging
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObligationPaymentsListView(generics.ListAPIView):
    """
    Listar todos los pagos de una obligación
    GET /api/properties/{property_id}/obligations/{obligation_id}/payments/
    """
    serializer_class = PropertyPaymentSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        obligation_id = self.kwargs.get('obligation_id')
        
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        # Validar que la obligación pertenezca a la propiedad
        get_object_or_404(Obligation, pk=obligation_id, property_id=property_id)
        
        return PropertyPayment.objects.filter(obligation_id=obligation_id)


class ObligationPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Ver, editar o eliminar un pago específico de una obligación
    GET /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
    PUT/PATCH /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
    DELETE /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
    """
    serializer_class = PropertyPaymentSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        obligation_id = self.kwargs.get('obligation_id')
        
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        # Validar que la obligación pertenezca a la propiedad
        get_object_or_404(Obligation, pk=obligation_id, property_id=property_id)
        
        return PropertyPayment.objects.filter(obligation_id=obligation_id)
    
    def get_object(self):
        payment_id = self.kwargs.get('payment_id')
        return get_object_or_404(self.get_queryset(), pk=payment_id)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'message': 'Payment deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


# ========== DASHBOARD - ESTADÍSTICAS GENERALES ==========

class DashboardView(APIView):
    """
    Vista de Dashboard con estadísticas del sistema
    Solo accesible para administradores
    
    ENDPOINT:
    GET /api/dashboard/
    
    RESPUESTA:
    {
        "obligations": {
            "total_count": 45,
            "total_amount": 15000000.00,
            "total_paid": 8500000.00,
            "pending": 6500000.00,
            "upcoming_due": 3
        },
        "properties": {
            "total": 12,
            "by_use": [
                {"use": "rental", "count": 8},
                {"use": "personal", "count": 4}
            ]
        },
        "rentals": {
            "active": 6,
            "available": 2,
            "ending_soon": 1
        },
        "monthly_summary": {
            "rental_income": 4500000.00,
            "obligation_payments": 1200000.00,
            "repair_costs": 300000.00,
            "net": 3000000.00
        }
    }
    
    FUNCIONAMIENTO:
    - Calcula estadísticas en tiempo real
    - Útil para mostrar en pantalla principal
    - Puede ser llamado cada vez que el usuario accede al dashboard
    """
    permission_classes = [IsAdminUser]  # Solo admins
    
    def get(self, request):
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)
        
        # ========== 1. OBLIGACIONES ==========
        total_obligations = Obligation.objects.filter(property__is_deleted__isnull=True).count()
        total_obligation_amount = Obligation.objects.filter(property__is_deleted__isnull=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Total pagado en obligaciones
        total_paid_obligations = PropertyPayment.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_obligations = total_obligation_amount - total_paid_obligations
        
        # Obligaciones que vencen en los próximos 7 días
        upcoming_obligations = Obligation.objects.filter(property__is_deleted__isnull=True,
            due_date__gte=today,
            due_date__lte=today + timedelta(days=7)
        ).count()
        
        # ========== 1.1 OBLIGACIONES DEL MES ==========
        # Obligaciones del mes actual (por fecha de vencimiento)
        # NOTA: Incluye TODAS las obligaciones del mes, no solo las que ya vencieron
        last_day_of_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        month_obligations = Obligation.objects.filter(property__is_deleted__isnull=True,
            due_date__gte=first_day_of_month,
            due_date__lte=last_day_of_month  # Hasta el último día del mes
        )
        
        month_obligations_count = month_obligations.count()
        month_obligations_amount = month_obligations.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Pagos de obligaciones del mes (pagos realizados este mes)
        month_obligations_paid = PropertyPayment.objects.filter(
            
            date__gte=first_day_of_month,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_obligations_pending = month_obligations_amount - month_obligations_paid
        
        # Obligaciones del mes que vencen en los próximos 7 días
        # Solo cuenta las que están dentro del mes Y vencen en los próximos 7 días
        month_upcoming = month_obligations.filter(
            due_date__gte=today,
            due_date__lte=today + timedelta(days=7)
        ).count()
        
        # ========== 2. PROPIEDADES ==========
        # Solo contar propiedades activas (no soft-deleted)
        total_properties = Property.objects.filter(is_deleted__isnull=True).count()
        properties_by_use = Property.objects.filter(is_deleted__isnull=True).values('use').annotate(count=Count('id'))
        
        # ========== 3. RENTALS ==========
        from apps.rentals.models import Rental, RentalPayment
        
        occupied_rentals = Rental.objects.filter(
            status='occupied',
            property__is_deleted__isnull=True
        ).count()
        
        # Propiedades de rental sin rental activo (solo activas)
        available_properties = Property.objects.filter(
            use='rental',
            is_deleted__isnull=True  # Excluir soft-deleted
        ).exclude(
            rentals__status='occupied'
        ).distinct().count()
        
        # Rentals que terminan en los próximos 15 días
        upcoming_rental_ends = Rental.objects.filter(
            status='occupied',
            property__is_deleted__isnull=True,
            check_out__gte=today,
            check_out__lte=today + timedelta(days=15)
        ).count()
        
        # Estadísticas detalladas por tipo de rental (30 días para ending_soon)
        ending_soon_date = today + timedelta(days=15)
        
        # Monthly properties
        # Ocupadas: propiedades con rental_type='monthly' que tienen un rental activo
        monthly_occupied = Property.objects.filter(
            use='rental',
            rental_type='monthly',
            is_deleted__isnull=True,
            rentals__status='occupied'
        ).distinct().count()
        
        # Disponibles: propiedades con rental_type='monthly' sin rental activo
        monthly_available = Property.objects.filter(
            use='rental',
            rental_type='monthly',
            is_deleted__isnull=True
        ).exclude(
            rentals__status='occupied'
        ).distinct().count()
        
        monthly_ending_soon = Rental.objects.filter(
            rental_type='monthly',
            status='occupied',
            property__is_deleted__isnull=True,
            check_out__gte=today,
            check_out__lte=ending_soon_date
        ).count()
        
        # Airbnb properties
        # Ocupadas: propiedades con rental_type='airbnb' que tienen un rental activo
        airbnb_occupied = Property.objects.filter(
            use='rental',
            rental_type='airbnb',
            is_deleted__isnull=True,
            rentals__status='occupied'
        ).distinct().count()
        
        # Disponibles: propiedades con rental_type='airbnb' sin rental activo
        airbnb_available = Property.objects.filter(
            use='rental',
            rental_type='airbnb',
            is_deleted__isnull=True
        ).exclude(
            rentals__status='occupied'
        ).distinct().count()
        
        airbnb_ending_soon = Rental.objects.filter(
            rental_type='airbnb',
            status='occupied',
            property__is_deleted__isnull=True,
            check_out__gte=today,
            check_out__lte=ending_soon_date
        ).count()
        
        # ========== 4. RESUMEN FINANCIERO DEL MES ==========
        # Ingresos: pagos de rentals
        monthly_rental_payments = RentalPayment.objects.filter(
            date__gte=first_day_of_month,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Gastos: pagos de obligaciones
        monthly_obligation_payments = PropertyPayment.objects.filter(
            date__gte=first_day_of_month,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Gastos: reparaciones
        from apps.maintenance.models import Repair
        monthly_repairs = Repair.objects.filter(
            date__gte=first_day_of_month
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        # Neto del mes
        monthly_net = monthly_rental_payments - monthly_obligation_payments - monthly_repairs
        
        return Response({
            'obligations': {
                'total_count': total_obligations,
                'total_amount': float(total_obligation_amount),
                'total_paid': float(total_paid_obligations),
                'pending': float(pending_obligations),
                'upcoming_due': upcoming_obligations
            },
            'obligations_month': {
                'total_count': month_obligations_count,
                'total_amount': float(month_obligations_amount),
                'total_paid': float(month_obligations_paid),
                'pending': float(month_obligations_pending),
                'upcoming_due': month_upcoming
            },
            'properties': {
                'total': total_properties,
                'by_use': list(properties_by_use)
            },
            'rentals': {
                'occupied': occupied_rentals,
                'available': available_properties,
                'ending_soon': upcoming_rental_ends,
                # Estadísticas detalladas por tipo
                'monthly_occupied': monthly_occupied,
                'monthly_available': monthly_available,
                'monthly_ending_soon': monthly_ending_soon,
                'airbnb_occupied': airbnb_occupied,
                'airbnb_available': airbnb_available,
                'airbnb_ending_soon': airbnb_ending_soon
            },
            'monthly_summary': {
                'rental_income': float(monthly_rental_payments),
                'obligation_payments': float(monthly_obligation_payments),
                'repair_costs': float(monthly_repairs),
                'net': float(monthly_net)
            }
        })


# ========== NOTIFICACIONES ==========

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para notificaciones del sistema
    
    ENDPOINTS:
    - GET /api/notifications/ - Listar no leídas (paginado)
    - GET /api/notifications/?is_read=true - Listar todas las leídas
    - GET /api/notifications/{id}/ - Ver detalle
    - POST /api/notifications/ - Crear notificación manual
    - DELETE /api/notifications/{id}/ - Eliminar
    
    ACCIONES ESPECIALES:
    - POST /api/notifications/{id}/mark_as_read/ - Marcar una como leída
    - POST /api/notifications/mark_all_as_read/ - Marcar todas como leídas
    - GET /api/notifications/unread_count/ - Contar no leídas
    
    FILTROS:
    - ?type=obligation_due - Por tipo
    - ?priority=high - Por prioridad
    - ?is_read=false - No leídas (default)
    - ?created_from=2026-02-01 - Desde fecha
    
    ORDENAMIENTO:
    - ?ordering=-created_at - Más recientes primero (default)
    - ?ordering=priority - Por prioridad
    
    FUNCIONAMIENTO:
    1. Crear notificación:
       POST /api/notifications/
       {
           "type": "obligation_due",
           "priority": "high",
           "title": "Pago de luz",
           "message": "Vence en 3 días",
           "obligation": 1
       }
    
    2. Marcar como leída:
       POST /api/notifications/5/mark_as_read/
    
    3. Consultar contador:
       GET /api/notifications/unread_count/
       → {"count": 5}
    """
    queryset = Notification.objects.all()
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NotificationFilter
    ordering_fields = ['created_at', 'priority', 'type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def get_queryset(self):
        """Por defecto muestra solo no leídas"""
        queryset = super().get_queryset()
        
        # Si no se especifica is_read en los filtros, mostrar solo no leídas
        if 'is_read' not in self.request.query_params:
            queryset = queryset.filter(is_read=False)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marcar una notificación como leída
        
        POST /api/notifications/{id}/mark_as_read/
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Marcar todas las notificaciones como leídas
        
        POST /api/notifications/mark_all_as_read/
        """
        count = Notification.objects.filter(is_read=False).update(is_read=True)
        
        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Contar notificaciones no leídas
        
        GET /api/notifications/unread_count/
        
        Útil para mostrar badge en el icono de notificaciones
        """
        count = Notification.objects.filter(is_read=False).count()
        
        return Response({
            'count': count
        })

