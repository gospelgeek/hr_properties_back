from rest_framework import serializers
from .models import Tenant, Rental, RentalPayment, MonthlyRental, AirbnbRental
from apps.properties.models import Property


class TenantSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = ['id', 'email', 'name', 'lastname', 'phone1', 'phone2', 'birth_year', 'observations', 'full_name']
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
    monthly_data = serializers.JSONField(required=False, write_only=True)
    airbnb_data = serializers.JSONField(required=False, write_only=True)
    
    class Meta:
        model = Rental
        exclude = ['property']
    
    def validate_monthly_data(self, value):
        """Validar y convertir monthly_data si viene como string"""
        if isinstance(value, str):
            import json
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("monthly_data debe ser un JSON válido")
        return value
    
    def validate_airbnb_data(self, value):
        """Validar y convertir airbnb_data si viene como string"""
        if isinstance(value, str):
            import json
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("airbnb_data debe ser un JSON válido")
        return value
    
    def validate(self, data):
        """Validar que el tipo de rental coincida con los datos proporcionados"""
        rental_type = data.get('rental_type')
        monthly_data = data.get('monthly_data')
        airbnb_data = data.get('airbnb_data')
        status = data.get('status', 'available')
        tenant = data.get('tenant')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        # Si NO hay tenant, status debe ser available
        if not tenant:
            if status != 'available':
                raise serializers.ValidationError({
                    'status': 'Si no hay inquilino, el estado debe ser "available".'
                })
            # check_in y check_out pueden ser None cuando no hay tenant
        else:
            # Si hay tenant, check_in y check_out son obligatorios
            if not check_in:
                raise serializers.ValidationError({
                    'check_in': 'Se requiere fecha de check-in cuando hay un inquilino asignado.'
                })
            if not check_out:
                raise serializers.ValidationError({
                    'check_out': 'Se requiere fecha de check-out cuando hay un inquilino asignado.'
                })
            # Si hay tenant, status debe ser occupied
            if status != 'occupied':
                raise serializers.ValidationError({
                    'status': 'Si hay un inquilino asignado, el estado debe ser "occupied".'
                })
        
        # Validar que monthly_data tenga los campos obligatorios
        if rental_type == 'monthly':
            if not monthly_data:
                raise serializers.ValidationError({
                    'monthly_data': 'Se requieren datos de arriendo mensual (deposit_amount, is_refundable)'
                })
            
            # Asegurar que monthly_data sea un diccionario
            if isinstance(monthly_data, str):
                import json
                try:
                    monthly_data = json.loads(monthly_data)
                    data['monthly_data'] = monthly_data
                except json.JSONDecodeError:
                    raise serializers.ValidationError({
                        'monthly_data': 'Debe ser un JSON válido'
                    })
            
            if 'deposit_amount' not in monthly_data:
                raise serializers.ValidationError({
                    'monthly_data': {'deposit_amount': 'Este campo es obligatorio para rentas mensuales'}
                })
            if 'is_refundable' not in monthly_data:
                raise serializers.ValidationError({
                    'monthly_data': {'is_refundable': 'Este campo es obligatorio para rentas mensuales'}
                })
        
        # Validar que airbnb_data tenga los campos obligatorios
        if rental_type == 'airbnb':
            if not airbnb_data:
                raise serializers.ValidationError({
                    'airbnb_data': 'Se requieren datos de Airbnb (deposit_amount, is_refundable)'
                })
            if 'deposit_amount' not in airbnb_data:
                raise serializers.ValidationError({
                    'airbnb_data': {'deposit_amount': 'Este campo es obligatorio para Airbnb'}
                })
            if 'is_refundable' not in airbnb_data:
                raise serializers.ValidationError({
                    'airbnb_data': {'is_refundable': 'Este campo es obligatorio para Airbnb'}
                })
        
        return data
    
    def create(self, validated_data):
        monthly_data = validated_data.pop('monthly_data', None)
        airbnb_data = validated_data.pop('airbnb_data', None)
        
        # Obtener el archivo si existe en el request
        request = self.context.get('request')
        url_files = None
        if request and request.FILES:
            url_files = request.FILES.get('monthly_data.url_files') or request.FILES.get('url_files')
        
        # Crear el rental
        rental = Rental.objects.create(**validated_data)
        
        # Crear el registro específico según el tipo
        if monthly_data:
            # Agregar el archivo si existe
            if url_files:
                monthly_data['url_files'] = url_files
            MonthlyRental.objects.create(rental=rental, **monthly_data)
        
        if airbnb_data:
            AirbnbRental.objects.create(rental=rental, **airbnb_data)
        
        return rental
