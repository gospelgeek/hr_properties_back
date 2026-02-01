from rest_framework import serializers
from .models import ObligationType, Obligation, PaymentMethod, PropertyPayment


class ObligationTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de obligaciones"""
    class Meta:
        model = ObligationType
        fields = '__all__'
        read_only_fields = ['id']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer para métodos de pago"""
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ['id']


class PropertyPaymentSerializer(serializers.ModelSerializer):
    """Serializer completo para pagos de obligaciones"""
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    obligation_name = serializers.CharField(source='obligation.entity_name', read_only=True)
    
    class Meta:
        model = PropertyPayment
        fields = '__all__'
        read_only_fields = ['id']


class PropertyPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos sin especificar obligation"""
    class Meta:
        model = PropertyPayment
        exclude = ['id', 'obligation']


class ObligationSerializer(serializers.ModelSerializer):
    """Serializer básico para obligaciones"""
    obligation_type_name = serializers.CharField(source='obligation_type.name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Obligation
        fields = '__all__'
        read_only_fields = ['id']


class ObligationDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con todos los pagos asociados"""
    obligation_type = ObligationTypeSerializer(read_only=True)
    payments = PropertyPaymentSerializer(many=True, read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    total_paid = serializers.SerializerMethodField()
    pending_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Obligation
        fields = [
            'id', 'property', 'property_name', 'obligation_type', 
            'entity_name', 'amount', 'due_date', 'temporality',
            'payments', 'total_paid', 'pending_amount'
        ]
        read_only_fields = ['id']
    
    def get_total_paid(self, obj):
        """Calcular total pagado de esta obligación"""
        return sum(payment.amount for payment in obj.payments.all())
    
    def get_pending_amount(self, obj):
        """Calcular monto pendiente"""
        total_paid = self.get_total_paid(obj)
        return obj.amount - total_paid


class ObligationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear obligaciones sin especificar property"""
    class Meta:
        model = Obligation
        exclude = ['property']
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data['amount'] <= 0:
            raise serializers.ValidationError({
                'amount': 'El monto debe ser mayor a 0'
            })
        return data
