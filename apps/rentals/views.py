from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone

from apps.users.permissions import IsAdminUser, IsAdminOrReadOnlyClient
from .models import Tenant, Rental, RentalPayment, MonthlyRental, AirbnbRental
from apps.properties.models import Property
from .serializers import (
    TenantSerializer, RentalSerializer, RentalDetailSerializer, 
    RentalCreateSerializer, RentalPaymentSerializer, RentalPaymentCreateSerializer,
    MonthlyRentalSerializer, AirbnbRentalSerializer
)


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAdminUser]  # Solo admins pueden gestionar tenants


class RentalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consultar rentals con filtros avanzados
    
    PERMISOS:
    - Admins: Acceso completo (CRUD)
    - Clientes: Solo lectura de sus propios rentals
    
    ENDPOINTS:
    - GET /api/rentals/ - Listar todos los rentals
    - GET /api/rentals/{id}/ - Ver detalle de un rental
    - GET /api/rentals/ending_soon/ - Rentals que terminan pronto
    
    FILTROS DISPONIBLES:
    - ?status=occupied - Filtrar por estado (occupied/available)
    - ?rental_type=monthly - Filtrar por tipo (monthly/airbnb)
    - ?ending_in_days=30 - Rentals que terminan en X días (solo aplica a status=occupied)
    
    EJEMPLOS:
    - GET /api/rentals/?status=occupied&rental_type=monthly
    - GET /api/rentals/?ending_in_days=15
    - GET /api/rentals/ending_soon/
    """
    queryset = Rental.objects.all()
    permission_classes = [IsAdminOrReadOnlyClient]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RentalDetailSerializer
        return RentalSerializer
    
    def get_queryset(self):
        """
        Aplicar filtros a la consulta de rentals
        Los clientes solo ven sus propios rentals
        """
        queryset = Rental.objects.all()
        
        # Filtrar por rol: clientes solo ven sus rentals
        if hasattr(self.request.user, 'userrole_set'):
            user_roles = self.request.user.userrole_set.values_list('role__name', flat=True)
            if 'cliente' in user_roles:
                tenant = Tenant.objects.filter(phone1=self.request.user.username).first()
                if tenant:
                    queryset = queryset.filter(tenant=tenant)
        
        # Filtro por status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filtro por rental_type
        rental_type = self.request.query_params.get('rental_type', None)
        if rental_type:
            queryset = queryset.filter(rental_type=rental_type)
        
        # Filtro por ending_in_days (solo para rentals ocupados)
        ending_in_days = self.request.query_params.get('ending_in_days', None)
        if ending_in_days:
            try:
                days = int(ending_in_days)
                today = timezone.now().date()
                end_date = today + timedelta(days=days)
                
                queryset = queryset.filter(
                    status='occupied',
                    check_out__gte=today,
                    check_out__lte=end_date
                )
            except ValueError:
                pass  # Ignorar si no es un número válido
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def ending_soon(self, request):
        """
        Obtener rentals que terminan pronto (próximos 30 días por defecto)
        
        GET /api/rentals/ending_soon/
        GET /api/rentals/ending_soon/?days=15
        GET /api/rentals/ending_soon/?rental_type=monthly
        
        Parámetros opcionales:
        - days: Número de días para considerar "pronto" (default: 30)
        - rental_type: Filtrar por tipo de rental (monthly/airbnb)
        """
        days = int(request.query_params.get('days', 30))
        rental_type = request.query_params.get('rental_type', None)
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        queryset = Rental.objects.filter(
            status='occupied',
            check_out__gte=today,
            check_out__lte=end_date
        )
        
        if rental_type:
            queryset = queryset.filter(rental_type=rental_type)
        
        serializer = RentalDetailSerializer(queryset, many=True, context={'request': request})
        
        return Response({
            'count': queryset.count(),
            'days': days,
            'rentals': serializer.data
        })
    
    @action(detail=True, methods=['get'], url_path='payments')
    def payments(self, request, pk=None):
        """
        📋 Obtener todos los pagos de un rental específico (SOLO LECTURA)
        
        ENDPOINT:
            GET /api/rentals/{id}/payments/
        
        PERMISOS:
            ✅ Admins: Pueden ver todos los pagos de cualquier rental
            ✅ Clientes: Solo pueden ver pagos de sus propios rentals
            ❌ Clientes NO pueden crear, editar ni eliminar pagos (solo admins)
        
        EJEMPLO DE RESPUESTA:
        {
            "count": 3,                    // Total de pagos realizados
            "total_paid": 4500000.00,      // Suma total de todos los pagos
            "rental": {                    // Información del rental
                "id": 5,
                "property": {
                    "id": 2,
                    "address": "Calle 123 #45-67"
                },
                "tenant": {
                    "id": 3,
                    "phone1": "3001234567",
                    "email": "tenant@example.com"
                },
                "rental_type": "monthly",
                "status": "occupied",
                "amount": 1500000.00,
                "check_in": "2026-01-01",
                "check_out": "2026-07-01"
            },
            "payments": [                 // Lista de todos los pagos
                {
                    "id": 12,
                    "date": "2026-02-01",
                    "amount": 1500000.00,
                    "payment_method": {
                        "id": 2,
                        "name": "transfer"
                    },
                    "voucher_url": "http://example.com/vouchers/voucher_12.pdf",
                    "notes": "Pago mes de febrero"
                },
                {
                    "id": 11,
                    "date": "2026-01-01",
                    "amount": 1500000.00,
                    "payment_method": {
                        "id": 1,
                        "name": "cash"
                    },
                    "voucher_url": null,
                    "notes": "Pago mes de enero"
                }
            ]
        }
        
        NOTA: Para crear, editar o eliminar pagos, el admin debe usar:
            POST   /api/properties/{property_id}/rentals/{rental_id}/add_payment/
            PATCH  /api/properties/{property_id}/rentals/{rental_id}/payments/{payment_id}/
            DELETE /api/properties/{property_id}/rentals/{rental_id}/payments/{payment_id}/
        """
        rental = self.get_object()  # Esto ya aplica las validaciones de permisos del get_queryset
        
        # Los clientes solo pueden ver pagos de sus propios rentals
        if hasattr(request.user, 'userrole_set'):
            user_roles = request.user.userrole_set.values_list('role__name', flat=True)
            if 'cliente' in user_roles:
                tenant = Tenant.objects.filter(phone1=request.user.username).first()
                if not tenant or rental.tenant != tenant:
                    return Response(
                        {'detail': 'No tienes permiso para ver estos pagos.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        # Obtener pagos del rental
        payments = RentalPayment.objects.filter(rental=rental).order_by('-date')
        
        # Calcular total pagado
        from django.db.models import Sum
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # Serializar
        payments_serializer = RentalPaymentSerializer(payments, many=True, context={'request': request})
        rental_serializer = RentalSerializer(rental, context={'request': request})
        
        return Response({
            'count': payments.count(),
            'total_paid': float(total_paid),
            'rental': rental_serializer.data,
            'payments': payments_serializer.data
        })


class PropertyAddRentalView(generics.CreateAPIView):
    """Vista para crear un rental asociado a una propiedad específica"""
    serializer_class = RentalCreateSerializer
    
    def get_property(self):
        """Obtener la propiedad a partir del ID en la URL"""
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    
    def create(self, request, *args, **kwargs):
        """Crear un rental asociado a la propiedad"""
        property_instance = self.get_property()
        
        # Validar que la propiedad sea de rental (ahora con mayúscula)
        if property_instance.use != 'rental':
            return Response({
                'error': f'This property is for "{property_instance.get_use_display()}" use. Only rental properties can have rentals.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que no haya un rental activo (occupied) en esta propiedad
        occupied_rental = Rental.objects.filter(
            property=property_instance,
            status='occupied'
        ).first()
        
        if occupied_rental:
            return Response({
                'error': f'Esta propiedad ya tiene un rental activo (occupied). Debes finalizar o cancelar el rental actual antes de crear uno nuevo.',
                'occupied_rental_id': occupied_rental.id,
                'tenant': occupied_rental.tenant.full_name
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad (status viene del request)
            rental = serializer.save(property=property_instance)
            # Devolver la respuesta con el serializer completo
            response_serializer = RentalDetailSerializer(rental, context={'request': request})
            status_msg = 'occupied' if rental.status == 'occupied' else 'available'
            return Response({
                'message': f'Rental creado exitosamente para {property_instance.name}. Estado: {status_msg}',
                'rental': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyRentalsListView(generics.ListAPIView):
    """Vista para listar todos los rentals de una propiedad"""
    serializer_class = RentalDetailSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return Rental.objects.filter(property_id=property_id)


class PropertyRentalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para ver, editar o eliminar un rental específico de una propiedad"""
    serializer_class = RentalDetailSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return Rental.objects.filter(property_id=property_id)
    
    def get_object(self):
        rental_id = self.kwargs.get('rental_id')
        return get_object_or_404(self.get_queryset(), pk=rental_id)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = RentalCreateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            response_serializer = RentalDetailSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Rental eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)


class RentalAddPaymentView(generics.CreateAPIView):
    """
    Vista para añadir un pago a un rental específico
    
    PERMISOS: Solo admins pueden crear pagos
    """
    serializer_class = RentalPaymentCreateSerializer
    permission_classes = [IsAdminUser]  # Solo admins pueden crear pagos
    
    def get_rental(self):
        property_id = self.kwargs.get('property_id')
        rental_id = self.kwargs.get('rental_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return get_object_or_404(Rental, pk=rental_id, property_id=property_id)
    
    def create(self, request, *args, **kwargs):
        rental_instance = self.get_rental()
        
        # Pasar rental al contexto para validación
        serializer = self.get_serializer(
            data=request.data, 
            context={'request': request, 'rental': rental_instance}
        )
        
        if serializer.is_valid():
            payment = serializer.save(rental=rental_instance)
            response_serializer = RentalPaymentSerializer(payment, context={'request': request})
            
            # Mensaje especial para Airbnb
            if rental_instance.rental_type == 'airbnb':
                message = f'Pago de Airbnb registrado exitosamente (Transferencia automática)'
            else:
                message = f'Pago añadido exitosamente al rental'
            
            return Response({
                'message': message,
                'payment': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RentalPaymentsListView(generics.ListAPIView):
    """
    Vista para listar todos los pagos de un rental
    
    PERMISOS: Admins y clientes pueden ver (cliente solo sus propios rentals)
    RECOMENDACIÓN: Usar GET /api/rentals/{id}/payments/ en su lugar
    """
    serializer_class = RentalPaymentSerializer
    permission_classes = [IsAdminOrReadOnlyClient]  # Lectura para clientes y admins
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        rental_id = self.kwargs.get('rental_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return RentalPayment.objects.filter(rental_id=rental_id, rental__property_id=property_id)


class RentalPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para ver, editar o eliminar un pago específico de un rental
    
    PERMISOS: Solo admins pueden editar/eliminar pagos
    """
    serializer_class = RentalPaymentSerializer
    permission_classes = [IsAdminUser]  # Solo admins pueden editar/eliminar pagos
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        rental_id = self.kwargs.get('rental_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return RentalPayment.objects.filter(rental_id=rental_id, rental__property_id=property_id)
    
    def get_object(self):
        payment_id = self.kwargs.get('payment_id')
        return get_object_or_404(self.get_queryset(), pk=payment_id)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Pago eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)


class RentalsDashboardStatsView(APIView):
    """Vista para obtener estadísticas de rentals para el dashboard
    
    Retorna contadores agrupados por tipo de rental (monthly/airbnb) y estado:
    - occupied (occupied): Rentals ocupados actualmente
    - available: Rentals disponibles
    - ending_soon: Rentals que terminan en los próximos 30 días
    
    Ejemplo de respuesta:
    {
        "rentals": {
            "monthly_occupied": 5,
            "monthly_available": 2,
            "monthly_ending_soon": 1,
            "airbnb_occupied": 8,
            "airbnb_available": 3,
            "airbnb_ending_soon": 2
        }
    }
    """
    
    def get(self, request):
        # Fecha límite para "ending soon" (próximos 30 días)
        today = timezone.now().date()
        ending_soon_date = today + timedelta(days=30)
        
        # Contadores para rentals mensuales
        monthly_occupied = Rental.objects.filter(
            rental_type='monthly',
            status='occupied'
        ).count()
        
        monthly_available = Rental.objects.filter(
            rental_type='monthly',
            status='available'
        ).count()
        
        monthly_ending_soon = Rental.objects.filter(
            rental_type='monthly',
            status='occupied',
            check_out__gte=today,
            check_out__lte=ending_soon_date
        ).count()
        
        # Contadores para rentals Airbnb
        airbnb_occupied = Rental.objects.filter(
            rental_type='airbnb',
            status='occupied'
        ).count()
        
        airbnb_available = Rental.objects.filter(
            rental_type='airbnb',
            status='available'
        ).count()
        
        airbnb_ending_soon = Rental.objects.filter(
            rental_type='airbnb',
            status='occupied',
            check_out__gte=today,
            check_out__lte=ending_soon_date
        ).count()
        
        return Response({
            "rentals": {
                "monthly_occupied": monthly_occupied,
                "monthly_available": monthly_available,
                "monthly_ending_soon": monthly_ending_soon,
                "airbnb_occupied": airbnb_occupied,
                "airbnb_available": airbnb_available,
                "airbnb_ending_soon": airbnb_ending_soon
            }
        })
