from django.db import models

from django.core.validators import MinValueValidator
from apps.properties.models import Property

class ObligationType(models.Model):
    """Tipos de obligaciones (impuestos, servicios, etc.)"""
    OBLIGATION_TYPE_CHOICES = [
        ('tax', 'Tax'),
        ('seguro', 'Insurance'),
        ('cuota', 'Fee')
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name='Name',
        choices=OBLIGATION_TYPE_CHOICES
    )
    
    class Meta:
        db_table = 'obligation_type'
        verbose_name = 'Obligation Type'
        verbose_name_plural = 'Obligation Types'
    
    def __str__(self):
        return self.get_name_display()

class Obligation(models.Model):
    """
    Obligaciones de una propiedad
    
    ⚠️ MANEJO DE RECURRENCIA (IMPORTANTE):
    ========================================
    Cada Obligation es UN REGISTRO ÚNICO para UN PERÍODO específico.
    NO se crean automáticamente nuevas obligaciones para el siguiente período.
    
    FLUJO:
    1. Crear obligation febrero: amount=580000, due_date='2026-02-15', temporality='monthly'
    2. Registrar pagos (puede ser parcial o completo)
    3. Para marzo: CREAR MANUALMENTE otra obligation nueva
    
    MEJORA FUTURA: Sistema de tareas programadas para crear automáticamente
    """
    TEMPORALITY_CHOICES = [
        ('monthly', 'Monthly'),
        ('bimonthly', 'Bimonthly'),
        ('quarterly', 'Quarterly'),
        ('biannual', 'Biannual'),
        ('annual', 'Annual'),
        ('one_time', 'One Time'),
        ('weekly', 'Weekly'),
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
        verbose_name='Obligation Type'
    )
    entity_name = models.CharField(max_length=255, verbose_name='Entity Name')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Amount'
    )
    due_date = models.DateField(verbose_name='Due Date')
    temporality = models.CharField(
        max_length=100,
        choices=TEMPORALITY_CHOICES,
        verbose_name='Temporality'
    )
    
    class Meta:
        db_table = 'obligation'
        verbose_name = 'Obligation'
        verbose_name_plural = 'Obligations'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.entity_name} - {self.property.name}"

class PaymentMethod(models.Model):
    """Métodos de pago disponibles"""
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('check', 'Check'),
        ('card', 'Card'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255,
        choices=PAYMENT_TYPES,
        unique=True,
        verbose_name='Name'
    )
    
    class Meta:
        db_table = 'payment_method'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
    
    def __str__(self):
        return self.get_name_display()

class PropertyPayment(models.Model):
    """Pagos de obligaciones de propiedades"""
    LOCATION_CHOICES = [('office', 'Office'), ('daycare', 'Daycare')]
    
    id = models.AutoField(primary_key=True)
    obligation = models.ForeignKey(
        Obligation,
        on_delete=models.CASCADE,
        db_column='id_obligation',
        related_name='payments',
        verbose_name='Obligation'
    )
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.PROTECT, 
        db_column='id_payment_method',
        verbose_name='Payment Method'
    )
    payment_location = models.CharField(
        max_length=255,
        default="office",
        choices=LOCATION_CHOICES,
        verbose_name='Payment Location'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Amount'
    )
    date = models.DateField(verbose_name='Payment Date')
    voucher_url = models.FileField(
        blank=True,
        db_column='voucher_url',
        verbose_name='Voucher URL'
    )
    
    class Meta:
        db_table = 'property_payment'
        verbose_name = 'Obligation Payment'
        verbose_name_plural = 'Obligation Payments'
        ordering = ['-date']
    
    def __str__(self):
        return f"Pago {self.amount} - {self.obligation.entity_name}"


class Notification(models.Model):
    """Notificaciones del sistema - Alertas y recordatorios"""
    NOTIFICATION_TYPES = [
        ('obligation_due', 'Obligation Due'),
        ('rental_ending', 'Rental Ending'),
        ('payment_overdue', 'Payment Overdue'),
        ('repair_scheduled', 'Repair Scheduled'),
        ('system', 'System'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.AutoField(primary_key=True)
    type = models.CharField(
        max_length=50, 
        choices=NOTIFICATION_TYPES,
        verbose_name='Type'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priority'
    )
    title = models.CharField(max_length=255, verbose_name='Title')
    message = models.TextField(verbose_name='Message')
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relaciones opcionales (puede estar relacionada con una obligación o rental)
    obligation = models.ForeignKey(
        Obligation, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"
