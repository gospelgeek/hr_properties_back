from rest_framework import serializers

from .models import (
    Vehicle,
    Responsible,
    VehicleDocument,
    VehicleImages,
    VehicleRepair,
    ObligationVehicleType,
    ObligationVehicle,
    VehiclePayment,
)

class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = ['id', 'vehicle', 'name', 'file']
        read_only_fields = ['id']


class VehicleDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = ['name', 'file']
        
class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = ['id', 'vehicle', 'image']
        read_only_fields = ['id']


class VehicleImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = ['image']


class ResponsibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsible
        fields = ['id', 'name', 'email', 'number']
        read_only_fields = ['id']


class ResponsibleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsible
        fields = ['name', 'email', 'number']


class VehicleRepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleRepair
        fields = ['id', 'vehicle', 'date','observation' ,'description', 'cost']
        read_only_fields = ['id']


class VehicleRepairCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleRepair
        fields = ['date', 'observation', 'description', 'cost']


class ObligationVehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObligationVehicleType
        fields = ['id', 'name']
        read_only_fields = ['id']


class VehiclePaymentSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)

    class Meta:
        model = VehiclePayment
        fields = ['id', 'obligation', 'payment_method', 'payment_method_name', 'date', 'amount', 'voucher']
        read_only_fields = ['id']


class VehiclePaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePayment
        fields = ['payment_method', 'date', 'amount', 'voucher']


class ObligationVehicleSerializer(serializers.ModelSerializer):
    obligation_type_name = serializers.CharField(source='obligation_type.name', read_only=True)
    payments = VehiclePaymentSerializer(many=True, read_only=True)
    total_paid = serializers.SerializerMethodField()
    pending = serializers.SerializerMethodField()
    is_fully_paid = serializers.SerializerMethodField()

    class Meta:
        model = ObligationVehicle
        fields = [
            'id',
            'vehicle',
            'entity_name',
            'obligation_type',
            'obligation_type_name',
            'due_date',
            'amount',
            'temporality',
            'file',
            'payments',
            'total_paid',
            'pending',
            'is_fully_paid',
        ]
        read_only_fields = ['id']

    def get_total_paid(self, obj):
        return str(sum(payment.amount for payment in obj.payments.all()))

    def get_pending(self, obj):
        total_paid = sum(payment.amount for payment in obj.payments.all())
        pending = obj.amount - total_paid
        return str(max(pending, 0))

    def get_is_fully_paid(self, obj):
        total_paid = sum(payment.amount for payment in obj.payments.all())
        return total_paid >= obj.amount


class ObligationVehicleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObligationVehicle
        fields = ['entity_name', 'obligation_type', 'due_date', 'amount', 'temporality', 'file']


class VehicleSerializer(serializers.ModelSerializer):
    documents = VehicleDocumentSerializer(many=True, read_only=True)
    images = VehicleImageSerializer(many=True, read_only=True)
    responsibles = ResponsibleSerializer(source='responsible', many=True, read_only=True)
    responsible_ids = serializers.PrimaryKeyRelatedField(
        source='responsible', queryset=Responsible.objects.all(), many=True, write_only=True, required=False
    )
    repairs = VehicleRepairSerializer(many=True, read_only=True)
    obligations = ObligationVehicleSerializer(source='obligations_vehicle', many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'owner',
            'type',
            'purchase_date',
            'purchase_price',
            'photo',
            'brand',
            'model',
            'documents',
            'images',
            'responsibles',
            'responsible_ids',
            'repairs',
            'obligations',
        ]
        read_only_fields = ['id']