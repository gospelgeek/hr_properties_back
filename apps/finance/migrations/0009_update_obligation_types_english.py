# Migration to update obligation types to English

from django.db import migrations


def update_obligation_types_to_english(apps, schema_editor):
    """Actualizar tipos de obligación a inglés completo"""
    ObligationType = apps.get_model('finance', 'ObligationType')
    
    # Actualizar registros existentes
    ObligationType.objects.filter(name='seguro').update(name='insurance')
    ObligationType.objects.filter(name='cuota').update(name='fee')
    
    # Asegurar que existan todos los tipos
    obligation_types = ['tax', 'insurance', 'fee']
    for obligation_type in obligation_types:
        ObligationType.objects.get_or_create(name=obligation_type)


def reverse_update(apps, schema_editor):
    """Revertir a español"""
    ObligationType = apps.get_model('finance', 'ObligationType')
    ObligationType.objects.filter(name='insurance').update(name='seguro')
    ObligationType.objects.filter(name='fee').update(name='cuota')


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_alter_notification_options_alter_obligation_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_obligation_types_to_english, reverse_update),
    ]
