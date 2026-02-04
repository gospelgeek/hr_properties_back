from django.db import models
from django.core.validators import MinValueValidator
from apps.properties.models import Property

class Repair(models.Model):
    """Reparaciones de propiedades"""
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        db_column='id_property',
        related_name='repairs'
    )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Cost'
    )
    date = models.DateField(verbose_name='Date')
    observation = models.TextField(blank=True, verbose_name='Observation')
    description = models.TextField(verbose_name='Description')
    
    class Meta:
        db_table = 'repair'
        verbose_name = 'Repair'
        verbose_name_plural = 'Repairs'
        ordering = ['-date']
    
    def __str__(self):
        return f"Reparación - {self.property.name} - {self.date}"