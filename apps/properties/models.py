from django.db import models
from django.utils import timezone
import os


def property_image_upload_to(instance, filename):
    """Organiza imágenes de propiedades en carpetas por ID de propiedad"""
    ext = os.path.splitext(filename)[1]
    # Si la propiedad ya existe, usar su ID, sino usar 'temp'
    property_id = instance.id if instance.id else 'temp'
    return f'property_{property_id}/images/main{ext}'


def property_law_upload_to(instance, filename):
    """Organiza documentos legales en carpetas por ID de propiedad"""
    # Sanitizar nombre del archivo
    safe_filename = filename.replace(' ', '_')
    return f'property_{instance.property.id}/laws/{safe_filename}'


def property_media_upload_to(instance, filename):
    """Organiza media de propiedades en carpetas por ID de propiedad"""
    safe_filename = filename.replace(' ', '_')
    return f'property_{instance.property.id}/media/{safe_filename}'


def enser_inventory_upload_to(instance, filename):
    """Organiza inventario de enseres en carpetas por ID de propiedad"""
    safe_filename = filename.replace(' ', '_')
    return f'property_{instance.property.id}/ensers/{safe_filename}'


class Property(models.Model):
    
    RENTAL_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('airbnb', 'Airbnb'),
      ]
    
    USE_CHOICES = [
        ('rental', 'Rental'),
        ('personal', 'Personal'),
        ('commercial', 'Commercial')
    ]
    TYPE_BUILDINGS_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('office', 'Office')
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Name')
    use = models.CharField(max_length=100, choices=USE_CHOICES, verbose_name='Use Type')
    rental_type = models.CharField(
        max_length=100,
        choices=RENTAL_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Rental Type',
        help_text='Required if use is rental (monthly or airbnb)',
        default='monthly'
    )
    address = models.CharField(max_length=255, verbose_name='Address')
    map_url = models.URLField(
        max_length=2000,
        blank=True,
        verbose_name='Google Maps URL',
        help_text='Google Maps embed URL (src from iframe)'
    )
    zip_code = models.CharField(max_length=20, verbose_name='Zip Code')
    type_building = models.CharField(max_length=100, choices=TYPE_BUILDINGS_CHOICES, verbose_name='Building Type')
    state = models.CharField(max_length=100, db_column='state', verbose_name='State', default='Unknown')
    city = models.CharField(max_length=100, verbose_name='City')
    image_url = models.FileField(
        upload_to=property_image_upload_to,
        max_length=500,
        blank=True,
        verbose_name='Featured Image',
        help_text='Main property image URL'
    )
    is_deleted = models.DateTimeField(
        null=True, 
        blank=True, 
        db_column='is_deleted',
        verbose_name='Deleted At'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'property'
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def soft_delete(self):
        """Soft delete: marca la propiedad como eliminada"""
        self.is_deleted = timezone.now()
        self.save()
    
    def restore(self):
        """Restaurar una propiedad eliminada"""
        self.is_deleted = None
        self.save()
    
    @property
    def is_active(self):
        """Verifica si la propiedad está activa"""
        return self.is_deleted is None

class PropertyDetails(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.OneToOneField(
        Property, 
        on_delete=models.CASCADE, 
        db_column='id_property',
        related_name='details'
    )
    bedrooms = models.IntegerField(verbose_name='Bedrooms', null=True, blank=True)
    bathrooms = models.IntegerField(verbose_name='Bathrooms', null=True, blank=True)
    half_bathrooms = models.IntegerField(verbose_name='Half Bathrooms', default=0, null=True, blank=True)
    floors = models.IntegerField(verbose_name='Floors', null=True, blank=True)
    observations = models.TextField(blank=True, verbose_name='Observations', help_text='Additional details about the property')
    buildings = models.IntegerField(default=1, verbose_name='Buildings', null=True, blank=True)
    
    class Meta:
        db_table = 'property_details'
        verbose_name = 'Detalle de Propiedad'
        verbose_name_plural = 'Detalles de Propiedades'
    
    def __str__(self):
        return f"Detalles de {self.property.name}"

class PropertyMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('document', 'Documento'),
    ]
    
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        db_column='id_property',
        related_name='media'
    )
    media_type = models.CharField(
        max_length=50, 
        choices=MEDIA_TYPE_CHOICES,
        verbose_name='Tipo de medio'
    )
    url = models.FileField(upload_to=property_media_upload_to, verbose_name='URL')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_media'
        verbose_name = 'Medio de Propiedad'
        verbose_name_plural = 'Medios de Propiedades'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.media_type} - {self.property.name}"

class PropertyLaw(models.Model):
    """Nueva tabla para regulaciones y leyes de propiedades"""
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='laws'
    )
    entity_name = models.CharField(max_length=255, verbose_name='Nombre de entidad')
    url = models.FileField(upload_to=property_law_upload_to, blank=True, verbose_name='URL del documento')
    original_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        db_column='original_amount',
        verbose_name='Monto original'
    )
    legal_number = models.CharField(max_length=100, verbose_name='Número legal')
    is_paid = models.BooleanField(default=False, db_column='is_paid', verbose_name='Está pagado')
    
    class Meta:
        db_table = 'property_law'
        verbose_name = 'Ley de Propiedad'
        verbose_name_plural = 'Leyes de Propiedades'
    
    def __str__(self):
        return f"{self.entity_name} - {self.property.name}"

class Enser(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Nombre')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    condition = models.CharField(
        max_length=100, 
        choices=CONDITION_CHOICES,
        verbose_name='Condición'
    )
    
    class Meta:
        db_table = 'enser'
        verbose_name = 'Enser'
        verbose_name_plural = 'Enseres'
    
    def __str__(self):
        return self.name

class EnserInventory(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        db_column='id_property',
        related_name='inventory'
    )
    enser = models.ForeignKey(
        Enser, 
        on_delete=models.CASCADE, 
        db_column='id_enser'
    )
    url_media = models.FileField(
        upload_to=enser_inventory_upload_to,
        blank=True, 
        null=True, 
        db_column='url_media',
        verbose_name='Archivos del inventario'
    )
    
    class Meta:
        db_table = 'enser_inventory'
        verbose_name = 'Inventario de Enser'
        verbose_name_plural = 'Inventarios de Enseres'
        unique_together = ('property', 'enser')
    
    def __str__(self):
        return f"{self.enser.name} - {self.property.name}"