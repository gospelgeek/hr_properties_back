from rest_framework import serializers
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia
from apps.maintenance.models import Repair


class PropertyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDetails
        exclude = ['id', 'property']  # Excluimos property porque se asigna automáticamente


class PropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ['id', 'media_type', 'url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class PropertyMediaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear media sin especificar property"""
    class Meta:
        model = PropertyMedia
        exclude = ['id', 'property', 'uploaded_at']


class PropertySerializer(serializers.ModelSerializer):
    details = PropertyDetailsSerializer(required=False)
    media = PropertyMediaSerializer(many=True, read_only=True)  # Solo lectura
    
    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'use',
            'address',
            'ubication',
            'zip_code',
            'type_building',
            'city',
            'created_at',
            'updated_at',
            'details',
            'media'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crear propiedad con detalles"""
        details_data = validated_data.pop('details', None)
        
        property_instance = Property.objects.create(**validated_data)
        
        # Crear detalles si se proporcionaron
        if details_data:
            PropertyDetails.objects.create(property=property_instance, **details_data)
        
        return property_instance
    
    def update(self, instance, validated_data):
        """Actualizar propiedad y detalles"""
        details_data = validated_data.pop('details', None)
        
        # Actualizar campos de la propiedad
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar o crear detalles
        if details_data:
            PropertyDetails.objects.update_or_create(
                property=instance,
                defaults=details_data
            )
        
        return instance


class PropertyLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyLaw
        fields = '__all__'


class EnserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enser
        fields = '__all__'


class EnserInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnserInventory
        fields = '__all__'


class EnserInventoryDetailSerializer(serializers.ModelSerializer):
    """Serializer anidado que incluye los datos completos del enser"""
    enser = EnserSerializer(read_only=True)
    
    class Meta:
        model = EnserInventory
        fields = ['id', 'enser', 'url_media']


class RepairSerializer(serializers.ModelSerializer):
    """Serializer para mostrar reparaciones"""
    class Meta:
        model = Repair
        fields = ['id', 'cost', 'date', 'observation', 'description']


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con detalles, media, inventario de enseres y reparaciones"""
    details = PropertyDetailsSerializer(required=False)
    media = PropertyMediaSerializer(many=True, read_only=True)
    inventory = EnserInventoryDetailSerializer(many=True, read_only=True)
    repairs = RepairSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'use',
            'address',
            'ubication',
            'zip_code',
            'type_building',
            'city',
            'created_at',
            'updated_at',
            'details',
            'media',
            'inventory',
            'repairs'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Serializer completo de PropertyMedia (con todos los campos) para lectura
class PropertyMediaListSerializer(serializers.ModelSerializer):
    """Serializer completo para listar media con información de la propiedad"""
    class Meta:
        model = PropertyMedia
        fields = '__all__'