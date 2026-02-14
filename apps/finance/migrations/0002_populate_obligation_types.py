# Generated manually for data population

from django.db import migrations


def create_initial_obligation_types(apps, schema_editor):
    """Crear los tipos de obligación iniciales basados en OBLIGATION_TYPE_CHOICES"""
    ObligationType = apps.get_model('finance', 'ObligationType')
    
    # Tipos basados en OBLIGATION_TYPE_CHOICES del modelo
    obligation_types = [
        ('tax', 'Tax'),
        ('insurance', 'Insurance'),
        ('fee', 'Fee'),
    ]
    
    for code, label in obligation_types:
        ObligationType.objects.get_or_create(
            name=code,
            defaults={'name': code}
        )


def reverse_population(apps, schema_editor):
    """Eliminar los tipos creados si se revierte la migración"""
    ObligationType = apps.get_model('finance', 'ObligationType')
    ObligationType.objects.filter(name__in=['tax', 'insurance', 'fee']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),  # Asegúrate de que este sea el nombre de tu primera migración
    ]

    operations = [
        migrations.RunPython(create_initial_obligation_types, reverse_population),
    ]
