from django.db import models

from django.core.validators import MinValueValidator
from apps.properties.models import Property
from apps.finance.models import PaymentMethod

class Tenant(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name='Correo electrónico')
    name = models.CharField(max_length=255, verbose_name='Nombre')
    lastname = models.CharField(max_length=255, verbose_name='Apellido')
    phone1 = models.CharField(max_length=20, verbose_name='Teléfono 1')
    phone2 = models.CharField(max_length=20, blank=True, verbose_name='Teléfono 2')
    observations = models.TextField(blank=True, verbose_name='Observaciones')
    
    class Meta:
        db_table = 'tenant'
        verbose_name = 'Inquilino'
        verbose_name_plural = 'Inquilinos'
    
    def __str__(self):
        return f"{self.name} {self.lastname}"
    
    @property
    def full_name(self):
        return f"{self.name} {self.lastname}"

class Rental(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('pending', 'Pendiente'),
    ]
    
    RENTAL_TYPE_CHOICES = [
        ('monthly', 'Mensual'),
        ('airbnb', 'Airbnb'),
        ('daily', 'Diario'),
    ]
    
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        db_column='id_property',
        related_name='rentals'
    )
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        db_column='id_tenant',
        related_name='rentals'
    )
    rental_type = models.CharField(
        max_length=100, 
        choices=RENTAL_TYPE_CHOICES,
        verbose_name='Tipo de arriendo'
    )
    check_in = models.DateField(verbose_name='Fecha de entrada')
    check_out = models.DateField(verbose_name='Fecha de salida')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Monto'
    )
    people_count = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Número de personas'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rental'
        verbose_name = 'Arriendo'
        verbose_name_plural = 'Arriendos'
        ordering = ['-check_in']
    
    def __str__(self):
        return f"{self.property.name} - {self.tenant.full_name} ({self.status})"

class RentalPayment(models.Model):
    """Pagos de arriendos - Mejorado con más campos"""
    id = models.AutoField(primary_key=True)
    rental = models.ForeignKey(
        Rental, 
        on_delete=models.CASCADE, 
        db_column='id_rental',
        related_name='payments'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        db_column='id_paymentMethod',
        verbose_name='Método de pago'
    )
    payment_location = models.CharField(max_length=255, verbose_name='Lugar de pago')
    date = models.DateField(verbose_name='Fecha de pago')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Monto'
    )
    voucher_url = models.URLField(
        blank=True,
        db_column='voucher_url',
        verbose_name='URL del comprobante'
    )
    
    class Meta:
        db_table = 'rental_payment'
        verbose_name = 'Pago de Arriendo'
        verbose_name_plural = 'Pagos de Arriendos'
        ordering = ['-date']
    
    def __str__(self):
        return f"Pago {self.amount} - {self.rental}"

class MonthlyRental(models.Model):
    """Arriendos mensuales - Ahora con is_refundable"""
    id = models.AutoField(primary_key=True)
    rental = models.ForeignKey(
        Rental, 
        on_delete=models.CASCADE, 
        db_column='id_rental',
        related_name='monthly_records'
    )
    deposit_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='depositAmount',
        verbose_name='Monto de depósito'
    )
    is_refundable = models.BooleanField(
        default=True,
        db_column='is_refundable',
        verbose_name='Es reembolsable'
    )
    url_files = models.URLField(
        blank=True,
        db_column='urlFiles',
        verbose_name='URL de archivos'
    )
    
    class Meta:
        db_table = 'monthly_rental'
        verbose_name = 'Arriendo Mensual'
        verbose_name_plural = 'Arriendos Mensuales'
    
    def __str__(self):
        return f"Mensual - {self.rental}"

class AirbnbRental(models.Model):
    """Arriendos Airbnb"""
    id = models.AutoField(primary_key=True)
    rental = models.ForeignKey(
        Rental, 
        on_delete=models.CASCADE, 
        db_column='id_rental',
        related_name='airbnb_records'
    )
    is_paid = models.BooleanField(
        default=False,
        db_column='is_paid(bool)',
        verbose_name='Está pagado'
    )
    
    class Meta:
        db_table = 'airbnb_rental'
        verbose_name = 'Arriendo Airbnb'
        verbose_name_plural = 'Arriendos Airbnb'
    
    def __str__(self):
        return f"Airbnb - {self.rental}"
