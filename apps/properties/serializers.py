from rest_framework import serializers
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia


class PropertyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDetails
        exclude = ['id', 'property']  # Excluimos property porque se asigna automáticamente


class PropertySerializer(serializers.ModelSerializer):
    details = PropertyDetailsSerializer(required=False)
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crear propiedad con detalles en una sola operación"""
        details_data = validated_data.pop('details', None)
        property_instance = Property.objects.create(**validated_data)
        
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


class PropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = '__all__'