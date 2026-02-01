from rest_framework import serializers
from .models import Tenant, Rental, RentalPayment, MonthlyRental, AirbnbRental
from apps.properties.models import Property


class TenantSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = ['id', 'email', 'name', 'lastname', 'phone1', 'phone2', 'observations', 'full_name']
        read_only_fields = ['id']


class MonthlyRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyRental
        exclude = ['id', 'rental']


class AirbnbRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirbnbRental
        exclude = ['id', 'rental']


class RentalPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalPayment
        fields = '__all__'
        read_only_fields = ['id']


class RentalPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos sin especificar rental
    
    Validación especial: Si el rental es de tipo Airbnb, 
    automáticamente asigna el método de pago "transferencia"
    """
    class Meta:
        model = RentalPayment
        exclude = ['id', 'rental']
    
    def validate(self, data):
        """
        Validar que si es Airbnb, el método de pago sea transferencia.
        Si no se especifica método de pago en Airbnb, lo asigna automáticamente.
        """
        # Obtener el rental del contexto (será asignado en la vista)
        rental = self.context.get('rental')
        
        if rental and rental.rental_type == 'airbnb':
            # Buscar el método de pago "transferencia"
            from apps.finance.models import PaymentMethod
            
            # Si no se proporcionó payment_method, asignar transferencia automáticamente
            if 'payment_method' not in data or data['payment_method'] is None:
                try:
                    transfer_method = PaymentMethod.objects.filter(
                        name__icontains='transfer'
                    ).first()
                    
                    if not transfer_method:
                        # Crear el método si no existe
                        transfer_method = PaymentMethod.objects.create(name='Transferencia')
                    
                    data['payment_method'] = transfer_method
                except Exception:
                    raise serializers.ValidationError({
                        'payment_method': 'Para Airbnb se requiere método de pago "Transferencia"'
                    })
            else:
                # Si se proporcionó, validar que sea transferencia
                payment_method = data['payment_method']
                if 'transfer' not in payment_method.name.lower():
                    raise serializers.ValidationError({
                        'payment_method': f'Los pagos de Airbnb deben ser por transferencia. Método actual: {payment_method.name}'
                    })
        
        return data


class RentalSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Rental
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class RentalDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con tenant, monthly/airbnb y payments"""
    tenant = TenantSerializer(read_only=True)
    monthly_records = MonthlyRentalSerializer(many=True, read_only=True)
    airbnb_records = AirbnbRentalSerializer(many=True, read_only=True)
    payments = RentalPaymentSerializer(many=True, read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Rental
        fields = [
            'id', 'property', 'property_name', 'tenant', 'rental_type',
            'check_in', 'check_out', 'amount', 'people_count', 'notes',
            'status', 'created_at', 'updated_at', 'monthly_records',
            'airbnb_records', 'payments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RentalCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear rentals con datos anidados de monthly/airbnb"""
    monthly_data = MonthlyRentalSerializer(required=False, write_only=True)
    airbnb_data = AirbnbRentalSerializer(required=False, write_only=True)
    
    class Meta:
        model = Rental
        exclude = ['property']
    
    def validate(self, data):
        """Validar que el tipo de rental coincida con los datos proporcionados"""
        rental_type = data.get('rental_type')
        monthly_data = data.get('monthly_data')
        airbnb_data = data.get('airbnb_data')
        status = data.get('status', 'disponible')
        tenant = data.get('tenant')
        
        # Validar que si status='ocupada', se requiere tenant
        if status == 'ocupada' and not tenant:
            raise serializers.ValidationError({
                'tenant': 'Se requiere un inquilino cuando el estado es "ocupada"'
            })
        
        # Validar que si hay tenant, el status debe ser 'ocupada'
        if tenant and status != 'ocupada':
            raise serializers.ValidationError({
                'status': 'Si hay un inquilino asignado, el estado debe ser "ocupada"'
            })
        
        if rental_type == 'monthly' and not monthly_data:
            raise serializers.ValidationError({
                'monthly_data': 'Se requieren datos de arriendo mensual para este tipo'
            })
        
        if rental_type == 'airbnb' and not airbnb_data:
            raise serializers.ValidationError({
                'airbnb_data': 'Se requieren datos de Airbnb para este tipo'
            })
        
        return data
    
    def create(self, validated_data):
        monthly_data = validated_data.pop('monthly_data', None)
        airbnb_data = validated_data.pop('airbnb_data', None)
        
        # Crear el rental
        rental = Rental.objects.create(**validated_data)
        
        # Crear el registro específico según el tipo
        if monthly_data:
            MonthlyRental.objects.create(rental=rental, **monthly_data)
        
        if airbnb_data:
            AirbnbRental.objects.create(rental=rental, **airbnb_data)
        
        return rental
