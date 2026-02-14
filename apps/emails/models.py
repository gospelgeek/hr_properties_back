from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AlertSent(models.Model):
    """
    Registro de alertas enviadas para evitar duplicados
    
    Este modelo registra cada vez que se envía una alerta, para que
    no se envíe el mismo tipo de alerta múltiples veces.
    
    Ejemplo:
    - Se envía alerta de "5_days" para Obligation ID=1 el 10/02
    - No se volverá a enviar alerta de "5_days" para esa Obligation
    - Pero SÍ se puede enviar alerta de "1_day" más adelante
    """
    
    ALERT_TYPES = [
        ('5_days', '5 Days Before'),
        ('1_day', '1 Day Before'),
        ('same_day', 'Same Day'),
    ]
    
    # Usar GenericForeignKey para relacionar con cualquier modelo
    # (Obligation, Rental, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name='Alert Type'
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Sent At')
    recipient_email = models.EmailField(verbose_name='Recipient Email')
    
    class Meta:
        db_table = 'alert_sent'
        verbose_name = 'Alert Sent'
        verbose_name_plural = 'Alerts Sent'
        unique_together = ['content_type', 'object_id', 'alert_type']
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.content_type} #{self.object_id}"
