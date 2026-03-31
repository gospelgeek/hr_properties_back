from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Count, Q, Sum
import calendar
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

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

    @staticmethod
    def _calculate_payment_status(rental, total_paid, expected_total):
        """Calcula el estado de pago a la fecha para mostrar si va al día."""
        today = timezone.now().date()
        total_paid = Decimal(total_paid or 0)
        expected_total = Decimal(expected_total or 0)
        monthly_amount = Decimal(rental.amount or 0)

        contract_months = None
        if rental.check_in and rental.check_out and rental.check_out > rental.check_in:
            contract_months = (rental.check_out.year - rental.check_in.year) * 12 + (rental.check_out.month - rental.check_in.month)
            if rental.check_out.day > rental.check_in.day:
                contract_months += 1
            contract_months = max(contract_months, 1)

        installments_due = 0
        expected_to_date = Decimal('0')

        if rental.rental_type == 'monthly' and rental.check_in and monthly_amount > 0:
            if today >= rental.check_in:
                start_date = rental.check_in
                anchor_day = start_date.day

                months_elapsed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
                installments_due = 0

                for month_offset in range(months_elapsed + 1):
                    target_month_index = (start_date.month - 1) + month_offset
                    target_year = start_date.year + (target_month_index // 12)
                    target_month = (target_month_index % 12) + 1
                    last_day_of_target_month = calendar.monthrange(target_year, target_month)[1]
                    due_day = min(anchor_day, last_day_of_target_month)
                    due_date = start_date.replace(year=target_year, month=target_month, day=due_day)

                    if due_date <= today:
                        installments_due += 1

                if contract_months is not None:
                    installments_due = min(installments_due, contract_months)
                installments_due = max(installments_due, 0)
                expected_to_date = monthly_amount * installments_due
            expected_to_date = min(expected_to_date, expected_total)
        elif rental.check_in and today >= rental.check_in:
            expected_to_date = expected_total

        overdue_amount = expected_to_date - total_paid
        if overdue_amount < 0:
            overdue_amount = Decimal('0')

        is_fully_paid = total_paid >= expected_total
        is_up_to_date = total_paid >= expected_to_date

        if is_fully_paid:
            status_label = 'fully_paid'
        elif is_up_to_date:
            status_label = 'up_to_date'
        elif expected_to_date > 0:
            status_label = 'overdue'
        else:
            status_label = 'not_due_yet'

        installments_paid_equivalent = Decimal('0')
        if monthly_amount > 0:
            installments_paid_equivalent = total_paid / monthly_amount
        return {
            'today': today.isoformat(),
            'monthly_amount': float(monthly_amount),
            'contract_months': contract_months,
            'installments_due': installments_due,
            'installments_paid_equivalent': float(installments_paid_equivalent),
            'expected_to_date': float(expected_to_date),
            'overdue_amount': float(overdue_amount),
            'is_up_to_date': is_up_to_date,
            'status_label': status_label,
        }
        
    
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
        
        # Calcular estado de pago usando total_amount cuando exista
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
        expected_total = rental.total_amount if rental.total_amount is not None else rental.amount
        pending = expected_total - total_paid
        if pending < 0:
            pending = 0
        is_fully_paid = total_paid >= expected_total
        payment_status = self._calculate_payment_status(rental, total_paid, expected_total)
        
        # Serializar
        payments_serializer = RentalPaymentSerializer(payments, many=True, context={'request': request})
        rental_serializer = RentalSerializer(rental, context={'request': request})
        
        return Response({
            'count': payments.count(),
            'total_paid': float(total_paid),
            'expected_total': float(expected_total),
            'pending': float(pending),
            'is_fully_paid': is_fully_paid,
            'payment_status': payment_status,
            'rental': rental_serializer.data,
            'payments': payments_serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def end_rental(self, request, pk=None):
        """
        Terminar un rental (eliminarlo) para que la propiedad quede libre (solo admins)
        
        ENDPOINT:
            POST /api/rentals/{id}/end_rental/
        
        PERMISOS:
            ✅ Solo admins
        
        USO:
            Cuando un rental termina y quieres liberar la propiedad para que pueda 
            ser alquilada nuevamente. Esto elimina el rental completamente.
        
        RESPUESTA:
        {
            "message": "Rental terminado. La propiedad Casa #123 está ahora disponible",
            "property": {
                "id": 2,
                "name": "Casa #123",
                "rental_type": "monthly"
            }
        }
        """
        rental = self.get_object()
        property_data = {
            'id': rental.property.id,
            'name': rental.property.name,
            'rental_type': rental.property.rental_type
        }
        
        # Eliminar el rental
        rental.delete()
        
        return Response({
            'message': f'Rental finished. Property {property_data["name"]} is now available',
            'property': property_data
        }, status=status.HTTP_200_OK)


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
        
        # Validar que la propiedad sea de rental o commercial
        if property_instance.use not in ['rental', 'commercial']:
            return Response({
                'error': f'This property is for "{property_instance.get_use_display()}" use. Only rental and commercial properties can have rentals.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que no exista ningún rental para esta propiedad
        # Una propiedad solo puede tener un rental (disponible u ocupado)
        existing_rental = Rental.objects.filter(
            property=property_instance
        ).first()
        
        if existing_rental:
            tenant_name = existing_rental.tenant.full_name if existing_rental.tenant else 'Sin inquilino asignado'
            return Response({
                'error': f'This property already has a rental ({existing_rental.get_status_display()}). You must end it before creating a new one.',
                'existing_rental_id': existing_rental.id,
                'tenant': tenant_name,
                'status': existing_rental.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad (status viene del request)
            rental = serializer.save(property=property_instance)
            # Devolver la respuesta con el serializer completo
            response_serializer = RentalDetailSerializer(rental, context={'request': request})
            status_msg = 'occupied' if rental.status == 'occupied' else 'available'
            return Response({
                'message': f'Rental created successfully for {property_instance.name}. Status: {status_msg}',
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
            rental = serializer.save()
            
            # Si ahora tiene tenant, check_in y check_out, cambiar automáticamente a occupied
            if rental.tenant and rental.check_in and rental.check_out:
                if rental.status != 'occupied':
                    rental.status = 'occupied'
                    rental.save()
            # Si se elimina el tenant, cambiar a available
            elif not rental.tenant:
                if rental.status != 'available':
                    rental.status = 'available'
                    rental.save()
            
            response_serializer = RentalDetailSerializer(rental, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Rental deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class RentalRemoveDocumentView(APIView):
    """Eliminar solo el documento de contrato de un rental mensual"""
    permission_classes = [IsAdminUser]

    def post(self, request, property_id, rental_id):
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        rental = get_object_or_404(Rental, pk=rental_id, property_id=property_id)

        if rental.rental_type != 'monthly':
            return Response({
                'error': 'Only monthly rentals have contract documents to remove.'
            }, status=status.HTTP_400_BAD_REQUEST)

        monthly_record = rental.monthly_records.first()
        if not monthly_record:
            return Response({
                'error': 'Monthly rental record not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if not monthly_record.url_files:
            return Response({
                'error': 'This rental has no document to remove.'
            }, status=status.HTTP_400_BAD_REQUEST)

        monthly_record.url_files.delete(save=False)
        monthly_record.url_files = None
        monthly_record.save(update_fields=['url_files'])

        return Response({
            'message': 'Rental document removed successfully',
            'rental_id': rental.id
        }, status=status.HTTP_200_OK)


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
            expected_total = rental_instance.total_amount if rental_instance.total_amount is not None else rental_instance.amount
            total_paid = rental_instance.payments.aggregate(total=Sum('amount'))['total'] or 0
            new_amount = serializer.validated_data['amount']

            if total_paid + new_amount > expected_total:
                return Response({
                    'error': 'Payment exceeds the rental expected amount',
                    'expected_total': expected_total,
                    'already_paid': total_paid,
                    'pending': expected_total - total_paid,
                    'attempted': new_amount
                }, status=status.HTTP_400_BAD_REQUEST)

            payment = serializer.save(rental=rental_instance)
            response_serializer = RentalPaymentSerializer(payment, context={'request': request})

            new_total_paid = total_paid + new_amount
            new_pending = expected_total - new_total_paid
            if new_pending < 0:
                new_pending = 0
            is_fully_paid = new_total_paid >= expected_total
            
            # Mensaje especial para Airbnb
            if rental_instance.rental_type == 'airbnb':
                message = f'Airbnb payment registered successfully (Automatic transfer)'
            else:
                message = f'Payment added successfully to rental'
            
            return Response({
                'message': message,
                'payment': response_serializer.data,
                'rental_status': {
                    'expected_total': expected_total,
                    'total_paid': new_total_paid,
                    'pending': new_pending,
                    'is_fully_paid': is_fully_paid
                }
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
        return Response({'message': 'Payment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


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
