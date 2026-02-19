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


class PropertyMediaUploadSerializer(serializers.Serializer):
    """Serializer para subir archivos a una propiedad existente"""
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        help_text="Lista de archivos a subir"
    )
    media_type = serializers.ChoiceField(
        choices=PropertyMedia.MEDIA_TYPE_CHOICES,
        default='image',
        help_text="Tipo de medio (image, video, document)"
    )


class PropertySerializer(serializers.ModelSerializer):
    details = PropertyDetailsSerializer(required=False)
    media = PropertyMediaSerializer(many=True, read_only=True)  # Solo lectura
    
    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'use',
            'rental_type',
            'address',
            'map_url',
            'zip_code',
            'type_building',
            'state',
            'city',
            'image_url',
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
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyLaw
        fields = ['id', 'property', 'entity_name', 'url', 'original_amount', 'legal_number', 'is_paid']
    
    def get_url(self, obj):
        """Devolver la URL completa del archivo si existe"""
        if obj.url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.url.url)
            return obj.url.url
        return None


class PropertyLawCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear PropertyLaw sin especificar property"""
    class Meta:
        model = PropertyLaw
        exclude = ['id', 'property']


class EnserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enser
        fields = '__all__'


class EnserInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnserInventory
        fields = '__all__'


class EnserInventoryCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear inventario de enseres sin especificar property"""
    class Meta:
        model = EnserInventory
        fields = ['enser', 'url_media']


class EnserCreateAndAddSerializer(serializers.Serializer):
    """Serializer para crear un nuevo enser y añadirlo al inventario de una propiedad"""
    name = serializers.CharField(max_length=255, help_text="Nombre del enser")
    price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Precio del enser")
    condition = serializers.ChoiceField(choices=Enser.CONDITION_CHOICES, help_text="Condición del enser")
    url_media = serializers.FileField(required=False, allow_null=True, help_text="Archivo del inventario (opcional)")


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
    """
    Serializer completo con detalles, media, inventario de enseres, reparaciones y leyes
    
    🔓 ACCESO PÚBLICO (usuarios no autenticados):
       - Solo para propiedades con rental_status=available
       - NO incluye información financiera sensible
       - Incluye: detalles, ubicación, multimedia, enseres (sin precios), reparaciones (sin costos)
    
    🔒 ACCESO ADMIN (usuarios autenticados como admin):
       - Acceso completo a toda la información
       - Incluye precios, costos, leyes/regulaciones, etc.
    """
    details = PropertyDetailsSerializer(required=False)
    media = PropertyMediaSerializer(many=True, read_only=True)
    inventory = EnserInventoryDetailSerializer(many=True, read_only=True)
    repairs = RepairSerializer(many=True, read_only=True)
    laws = PropertyLawSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'use',
            'rental_type',
            'address',
            'map_url',
            'zip_code',
            'type_building',
            'state',
            'city',
            'image_url',
            'created_at',
            'updated_at',
            'details',
            'media',
            'inventory',
            'repairs',
            'laws'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Personalizar la representación según el tipo de usuario:
        - Usuarios no autenticados: Ocultar información financiera sensible
        - Admins: Mostrar toda la información
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Si no hay request o el usuario NO está autenticado
        if not request or not request.user.is_authenticated:
            # Ocultar leyes/regulaciones (puede contener info sensible)
            data.pop('laws', None)
            
            # Ocultar precios de enseres (inventory)
            if 'inventory' in data and data['inventory']:
                for item in data['inventory']:
                    if 'enser' in item and item['enser']:
                        item['enser'].pop('price', None)
            
            # Ocultar costos de reparaciones
            if 'repairs' in data and data['repairs']:
                for repair in data['repairs']:
                    repair.pop('cost', None)
        
        return data


# Serializer completo de PropertyMedia (con todos los campos) para lectura
class PropertyMediaListSerializer(serializers.ModelSerializer):
    """Serializer completo para listar media con información de la propiedad"""
    class Meta:
        model = PropertyMedia
        fields = '__all__'