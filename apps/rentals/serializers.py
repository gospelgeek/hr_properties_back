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
    """Serializer para crear pagos sin especificar rental"""
    class Meta:
        model = RentalPayment
        exclude = ['id', 'rental']


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
