# Migration to add Zelle payment method

from django.db import migrations


def add_zelle_payment_method(apps, schema_editor):
    """Agregar Zelle como método de pago"""
    PaymentMethod = apps.get_model('finance', 'PaymentMethod')
    PaymentMethod.objects.get_or_create(name='zelle')


def remove_zelle_payment_method(apps, schema_editor):
    """Remover Zelle si se revierte la migración"""
    PaymentMethod = apps.get_model('finance', 'PaymentMethod')
    PaymentMethod.objects.filter(name='zelle').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_update_obligation_types_english'),
    ]

    operations = [
        migrations.RunPython(add_zelle_payment_method, remove_zelle_payment_method),
    ]
