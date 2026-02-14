# Generated manually for data population

from django.db import migrations


def create_payment_methods(apps, schema_editor):
    """Crear automáticamente los métodos de pago"""
    PaymentMethod = apps.get_model('finance', 'PaymentMethod')
    
    methods = [
        {'name': 'cash'},
        {'name': 'transfer'},
        {'name': 'check'},
        {'name': 'card'},
        {'name': 'zelle'},
    ]
    
    for method in methods:
        PaymentMethod.objects.get_or_create(**method)


def reverse_create_payment_methods(apps, schema_editor):
    """Eliminar los métodos de pago creados"""
    PaymentMethod = apps.get_model('finance', 'PaymentMethod')
    PaymentMethod.objects.filter(name__in=['cash', 'transfer', 'check', 'card', 'zelle']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_alter_paymentmethod_name_and_more'),
    ]

    operations = [
        migrations.RunPython(create_payment_methods, reverse_code=reverse_create_payment_methods),
    ]
