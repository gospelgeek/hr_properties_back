import os

from django.db import models
from apps.finance.models import PaymentMethod
# Create your models here.
''''
Carros:
A nombre de quién
Impuesto
Seguro, cambia cada año
Reparación
Fecha de compra - precio
Documentos
Quien esta a cargo
Tipo: comercial, deporte, uso permanente, agua
Ficha:

Foto
Marca modelo
Quien lo usa
etiqueta de Tipo
Filtros, por tipo - esto de filtros va en el frontend

'''
def vehicle_payment_voucher_upload_to(instance, filename):
    """Organiza vouchers de pagos en carpetas por ID de propiedad"""
    safe_filename = filename.replace(' ', '_')
    # Obtener el ID de la propiedad a través de la obligación
    vehicle_id = instance.obligation.vehicle.id
    return f'vehicle_{vehicle_id}/payments/{safe_filename}'


def _resolve_vehicle_id(instance):
    """Resuelve el ID del vehículo para modelos relacionados con Vehicle."""
    if getattr(instance, 'vehicle_id', None):
        return instance.vehicle_id

    vehicle = getattr(instance, 'vehicle', None)
    if vehicle and getattr(vehicle, 'id', None):
        return vehicle.id

    if getattr(instance, 'id', None):
        return instance.id

    return None


def vehicle_photo_upload_to(instance, filename):
    """Organiza fotos de vehículos en carpetas por ID de vehículo"""
    ext = os.path.splitext(filename)[1]
    vehicle_id = _resolve_vehicle_id(instance) or 'temp'
    return f'vehicle_{vehicle_id}/photos/photo{ext}'


def vehicle_doc_upload_to(instance, filename):
    """Organiza documentos de vehículos en carpetas por ID de vehículo"""
    safe_filename = filename.replace(' ', '_')

    vehicle_id = _resolve_vehicle_id(instance) or 'temp'
    return f'vehicle_{vehicle_id}/docs/{safe_filename}'

class Vehicle(models.Model):

    TYPE_CHOICES = [
        ('commercial', 'Commercial'),
        ('sport', 'Sport'),
        ('personal', 'Personal'),
        ('non_permanent_use', 'Non Permanent Use'),
        ('permanent_use', 'Permanent Use'),
        ('water', 'Water'),
    ]
    id = models.AutoField(primary_key=True)
    driver = models.CharField(max_length=255)  # a nombre de quien
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    vin_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    license_plate = models.CharField(max_length=20, unique=True, null=True, blank=True)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    photo = models.ImageField(upload_to=vehicle_photo_upload_to, blank=True, null=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    responsible = models.ManyToManyField('Responsible', related_name='vehicles', blank=True, null=True)


class VehicleDocument(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=vehicle_doc_upload_to)


class ObligationVehicleType(models.Model):
    OBLIGATION_TYPE_CHOICES = [
        ('tax', 'Tax'),
        ('insurance', 'Insurance'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name='Name',
        choices=OBLIGATION_TYPE_CHOICES
    )


class ObligationVehicle(models.Model):
    TEMPORALITY_CHOICES = [
        ('monthly', 'Monthly'),
        ('bimonthly', 'Bimonthly'),
        ('quarterly', 'Quarterly'),
        ('biannual', 'Biannual'),
        ('semiannual', 'Semiannual'),
        ('annual', 'Annual'),
        ('one_time', 'One Time'),
        ('weekly', 'Weekly'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Name')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='obligations_vehicle')
    entity_name = models.CharField(max_length=255, verbose_name='Entity Name')
    obligation_type = models.ForeignKey(ObligationVehicleType, on_delete=models.PROTECT, related_name='obligations_vehicle_type', blank=True, null=True)
    due_date = models.DateField(verbose_name='Due Date')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    temporality = models.CharField(max_length=100, choices=TEMPORALITY_CHOICES, verbose_name='Temporality')
    file = models.FileField(upload_to=vehicle_doc_upload_to, blank=True, null=True)
    
class VehiclePayment(models.Model):    
    id = models.AutoField(primary_key=True)
    obligation = models.ForeignKey(ObligationVehicle, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    voucher = models.FileField(upload_to=vehicle_payment_voucher_upload_to, blank=True, null=True)

class VehicleRepair(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='repairs')
    date = models.DateField()
    observation = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)


class Responsible(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  
    email = models.EmailField(blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    

class VehicleImages(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=vehicle_photo_upload_to)    
