from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ObligationType, Obligation, PaymentMethod, PropertyPayment
from .serializers import (
    ObligationTypeSerializer, 
    PaymentMethodSerializer,
    ObligationSerializer,
    ObligationDetailSerializer,
    ObligationCreateSerializer,
    PropertyPaymentSerializer,
    PropertyPaymentCreateSerializer
)
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
    """
    queryset = ObligationType.objects.all()
    serializer_class = ObligationTypeSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para métodos de pago
    - GET /api/payment-methods/ - Listar todos
    - POST /api/payment-methods/ - Crear nuevo
    - GET /api/payment-methods/{id}/ - Ver detalle
    - PUT/PATCH /api/payment-methods/{id}/ - Actualizar
    - DELETE /api/payment-methods/{id}/ - Eliminar
    """
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class ObligationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para todas las obligaciones del sistema
    - GET /api/obligations/ - Listar todas
    - GET /api/obligations/{id}/ - Ver detalle con pagos
    - PUT/PATCH /api/obligations/{id}/ - Actualizar
    - DELETE /api/obligations/{id}/ - Eliminar
    """
    queryset = Obligation.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ObligationDetailSerializer
        return ObligationSerializer


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
        return get_object_or_404(Property, pk=property_id)
    
    def create(self, request, *args, **kwargs):
        property_instance = self.get_property()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad
            obligation = serializer.save(property=property_instance)
            # Devolver respuesta completa
            response_serializer = ObligationDetailSerializer(obligation, context={'request': request})
            return Response({
                'message': f'Obligación creada exitosamente para {property_instance.name}',
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
            'message': 'Obligación eliminada exitosamente'
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
        return get_object_or_404(
            Obligation, 
            pk=obligation_id, 
            property_id=property_id
        )
    
    def create(self, request, *args, **kwargs):
        obligation_instance = self.get_obligation()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validar que no se pague más de lo debido
            total_paid = sum(p.amount for p in obligation_instance.payments.all())
            new_amount = serializer.validated_data['amount']
            
            if total_paid + new_amount > obligation_instance.amount:
                return Response({
                    'error': f'El pago excede el monto de la obligación',
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
                'message': 'Pago registrado exitosamente',
                'payment': response_serializer.data,
                'obligation_status': {
                    'total_amount': obligation_instance.amount,
                    'total_paid': new_total_paid,
                    'pending': obligation_instance.amount - new_total_paid,
                    'is_fully_paid': is_fully_paid
                }
            }, status=status.HTTP_201_CREATED)
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
            'message': 'Pago eliminado exitosamente'
        }, status=status.HTTP_204_NO_CONTENT)
