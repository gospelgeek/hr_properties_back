from django.db import models

from django.core.validators import MinValueValidator
from apps.properties.models import Property

class ObligationType(models.Model):
    """Tipos de obligaciones (impuestos, servicios, etc.)"""
    OBLIGATION_TYPE_CHOICES = [
        ('tax', 'Impuesto'),
        ('seguro', 'Seguro'),
        ('cuota', 'Cuota')
        ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, verbose_name='Nombre', choices=OBLIGATION_TYPE_CHOICES)
    
    class Meta:
        db_table = 'obligation_type'
        verbose_name = 'Tipo de Obligación'
        verbose_name_plural = 'Tipos de Obligaciones'
    
    def __str__(self):
        return self.name

class Obligation(models.Model):
    """Obligaciones de una propiedad"""
    TEMPORALITY_CHOICES = [
        ('monthly', 'Mensual'),
        ('bimonthly', 'Bimestral'),
        ('quarterly', 'Trimestral'),
        ('biannual', 'Semestral'),
        ('annual', 'Anual'),
        ('one_time', 'Una vez'),
        ('weekly', 'Semanal'),
    ]
    
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        db_column='id_property',
        related_name='obligations'
    )
    obligation_type = models.ForeignKey(
        ObligationType, 
        on_delete=models.PROTECT, 
        db_column='id_obligation_type',
        verbose_name='Tipo de obligación'
    )
    entity_name = models.CharField(max_length=255, verbose_name='Nombre de entidad')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Monto'
    )
    due_date = models.DateField(verbose_name='Fecha de vencimiento')
    temporality = models.CharField(
        max_length=100,
        choices=TEMPORALITY_CHOICES,
        verbose_name='Temporalidad'
    )
    
    class Meta:
        db_table = 'obligation'
        verbose_name = 'Obligación'
        verbose_name_plural = 'Obligaciones'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.entity_name} - {self.property.name}"

class PaymentMethod(models.Model):
    """Métodos de pago disponibles"""
    PAYMENT_TYPES = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
        ('card', 'Tarjeta'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nombre'
    )
    
    class Meta:
        db_table = 'payment_method'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
    
    def __str__(self):
        return self.name

class PropertyPayment(models.Model):
    """Pagos de obligaciones de propiedades"""
    id = models.AutoField(primary_key=True)
    obligation = models.ForeignKey(
        Obligation,
        on_delete=models.CASCADE,
        db_column='id_obligation',
        related_name='payments',
        verbose_name='Obligación'
    )
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.PROTECT, 
        db_column='id_paymentMethod',
        verbose_name='Método de pago'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Monto'
    )
    date = models.DateField(verbose_name='Fecha de pago')
    voucher_url = models.FileField(
        blank=True,
        db_column='voucher_url',
        verbose_name='URL del comprobante'
    )
    
    class Meta:
        db_table = 'property_payment'
        verbose_name = 'Pago de Obligación'
        verbose_name_plural = 'Pagos de Obligaciones'
        ordering = ['-date']
    
    def __str__(self):
        return f"Pago {self.amount} - {self.obligation.entity_name}"
