from rest_framework import serializers
from .models import Repair

class RepairSerializer(serializers.ModelSerializer):
    # Información de la propiedad para lectura
    property_name = serializers.CharField(source='property.name', read_only=True)
    property_address = serializers.CharField(source='property.address', read_only=True)
    property_city = serializers.CharField(source='property.city', read_only=True)
    
    class Meta:
        model = Repair
        fields = [
            'id',
            'property',
            'property_name',
            'property_address',
            'property_city',
            'cost',
            'date',
            'observation',
            'description'
        ]
        read_only_fields = ['id', 'property_name', 'property_address', 'property_city']

class RepairCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reparaciones sin mostrar el campo property"""
    class Meta:
        model = Repair
        fields = [
            'cost',
            'date',
            'observation',
            'description'
        ]