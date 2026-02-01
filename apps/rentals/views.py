from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action

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


class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RentalDetailSerializer
        return RentalSerializer


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
        
        # Validar que la propiedad sea de arrendamiento
        if property_instance.use != 'arrendamiento':
            return Response({
                'error': f'Esta propiedad es de uso "{property_instance.get_use_display()}". Solo las propiedades de arrendamiento pueden tener rentals.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que no haya un rental activo (ocupada) en esta propiedad
        active_rental = Rental.objects.filter(
            property=property_instance,
            status='ocupada'
        ).first()
        
        if active_rental:
            return Response({
                'error': f'Esta propiedad ya tiene un rental activo (ocupada). Debes finalizar o cancelar el rental actual antes de crear uno nuevo.',
                'active_rental_id': active_rental.id,
                'tenant': active_rental.tenant.full_name
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guardar asignando automáticamente la propiedad (status viene del request)
            rental = serializer.save(property=property_instance)
            # Devolver la respuesta con el serializer completo
            response_serializer = RentalDetailSerializer(rental, context={'request': request})
            status_msg = 'ocupada' if rental.status == 'ocupada' else 'disponible'
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
    """Vista para añadir un pago a un rental específico"""
    serializer_class = RentalPaymentCreateSerializer
    
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
    """Vista para listar todos los pagos de un rental"""
    serializer_class = RentalPaymentSerializer
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        rental_id = self.kwargs.get('rental_id')
        # Validar que la propiedad exista y no esté eliminada
        get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
        return RentalPayment.objects.filter(rental_id=rental_id, rental__property_id=property_id)


class RentalPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para ver, editar o eliminar un pago específico de un rental"""
    serializer_class = RentalPaymentSerializer
    
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
