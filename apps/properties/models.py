from django.db import models

# Create your models here.
from django.utils import timezone


class Property(models.Model):
    
    USE_CHOICES = [('arrendamiento', 'Arrendamiento'), ('personal', 'Personal'), ('comercial', 'Comercial')]
    TYPE_BUILDINGS_CHOICES = [('casa', 'Casa'), ('apartamento', 'Apartamento'), ('oficina', 'Oficina')]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Nombre')
    use = models.CharField(max_length=100, choices=USE_CHOICES, verbose_name='Uso')
    address = models.CharField(max_length=255, verbose_name='Dirección')
    ubication = models.CharField(max_length=255, verbose_name='Ubicación')
    zip_code = models.CharField(max_length=20, verbose_name='Código postal')
    type_building = models.CharField(max_length=100, choices=TYPE_BUILDINGS_CHOICES, verbose_name='Tipo de edificio')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    is_deleted = models.DateTimeField(
        null=True, 
        blank=True, 
        db_column='is_deleted',
        verbose_name='Fecha de eliminación'
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
    bedrooms = models.IntegerField(verbose_name='Habitaciones')
    bathrooms = models.IntegerField(verbose_name='Baños')
    floors = models.IntegerField(verbose_name='Pisos')
    observations = models.TextField(blank=True, verbose_name='Observaciones')
    buildings = models.IntegerField(default=1, verbose_name='Edificios')
    
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
    url = models.FileField(upload_to='property_media/', verbose_name='URL')
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
    url = models.FileField(upload_to='property_laws/', blank=True, verbose_name='URL del documento')
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
        ('new', 'Nuevo'),
        ('good', 'Bueno'),
        ('fair', 'Regular'),
        ('poor', 'Malo'),
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
        upload_to='enser_inventory/',
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