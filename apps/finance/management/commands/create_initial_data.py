"""
Comando para crear datos iniciales de Finance app
Ejecutar con: python manage.py create_initial_data
"""
from django.core.management.base import BaseCommand
from apps.finance.models import ObligationType, PaymentMethod


class Command(BaseCommand):
    help = 'Crea los datos iniciales para tipos de obligaciones y métodos de pago'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos iniciales...\n')
        
        # ========== TIPOS DE OBLIGACIONES ==========
        obligation_types = [
            {
                'name': 'Impuesto Predial',
                'description': 'Impuesto municipal sobre la propiedad'
            },
            {
                'name': 'Servicio Público',
                'description': 'Agua, luz, gas, internet, etc.'
            },
            {
                'name': 'Administración',
                'description': 'Cuota de administración del edificio o conjunto'
            },
            {
                'name': 'Seguro',
                'description': 'Seguros de la propiedad (incendio, terremoto, etc.)'
            },
            {
                'name': 'Cuota Extraordinaria',
                'description': 'Cuotas especiales para reparaciones o mejoras'
            },
            {
                'name': 'ICA',
                'description': 'Impuesto de Industria y Comercio'
            },
            {
                'name': 'Valorización',
                'description': 'Contribución por obras públicas'
            },
            {
                'name': 'Otro',
                'description': 'Otros tipos de obligaciones'
            },
        ]
        
        created_types = 0
        for type_data in obligation_types:
            obj, created = ObligationType.objects.get_or_create(
                name=type_data['name'],
                defaults={'description': type_data['description']}
            )
            if created:
                created_types += 1
                self.stdout.write(f'  ✓ Creado: {obj.name}')
            else:
                self.stdout.write(f'  - Ya existe: {obj.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Tipos de obligaciones: {created_types} creados, '
                f'{len(obligation_types) - created_types} ya existían'
            )
        )
        
        # ========== MÉTODOS DE PAGO ==========
        payment_methods = [
            'Efectivo',
            'Transferencia',
            'Cheque',
            'Tarjeta de Crédito',
            'Tarjeta de Débito',
            'Consignación',
        ]
        
        created_methods = 0
        for method_name in payment_methods:
            obj, created = PaymentMethod.objects.get_or_create(name=method_name)
            if created:
                created_methods += 1
                self.stdout.write(f'  ✓ Creado: {obj.name}')
            else:
                self.stdout.write(f'  - Ya existe: {obj.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Métodos de pago: {created_methods} creados, '
                f'{len(payment_methods) - created_methods} ya existían'
            )
        )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Datos iniciales creados exitosamente!'))
