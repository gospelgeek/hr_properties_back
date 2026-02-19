from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.rentals.models import Rental


class Command(BaseCommand):
    help = 'Actualiza el estado de los rentals a "available" cuando su check_out ha pasado'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Buscar rentals ocupados cuya fecha de check_out ya pasó
        expired_rentals = Rental.objects.filter(
            status='occupied',
            check_out__lt=today
        )
        
        updated_count = 0
        for rental in expired_rentals:
            rental.status = 'available'
            rental.save()
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Rental #{rental.id} ({rental.property.name}) actualizado a available'
                )
            )
        
        if updated_count == 0:
            self.stdout.write(
                self.style.WARNING('ℹ️  No hay rentals para actualizar')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ {updated_count} rental(s) actualizados a available'
                )
            )
