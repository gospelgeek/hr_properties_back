"""
Comando de Django para enviar alertas automáticas de:
- Obligaciones próximas a vencer
- Rentas próximas a vencer
- Pagos de rentas pendientes

USO:
    python manage.py send_due_alerts

PROGRAMACIÓN AUTOMÁTICA (Windows Task Scheduler):
    - Abre "Programador de tareas"
    - Crea tarea básica -> Nombre: "Alertas HR Properties"
    - Frecuencia: Diaria (ejecutar a las 8:00 AM)
    - Acción: Iniciar programa
    - Programa: C:\ruta\al\venv\Scripts\python.exe
    - Argumentos: C:\ruta\al\proyecto\manage.py send_due_alerts
    - Comenzar en: C:\ruta\al\proyecto\
    
PROGRAMACIÓN AUTOMÁTICA (Linux Cron):
    crontab -e
    0 8 * * * cd /ruta/al/proyecto && /ruta/al/venv/bin/python manage.py send_due_alerts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
import os
from apps.rentals.models import Rental, RentalPayment
from apps.finance.models import Obligation
from apps.emails.models import AlertSent
from apps.emails.utils import (
    send_obligation_alert,
    send_rental_due_alert,
    send_rental_payment_reminder
)


class Command(BaseCommand):
    help = 'Envía alertas por email de obligaciones y rentas próximas a vencer SOLO en días específicos (5 y 1 día antes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--alert-days',
            type=int,
            nargs='+',
            default=[5, 1],
            help='Días específicos para enviar alertas (default: 5 y 1 día antes). Ejemplo: --alert-days 5 1'
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        alert_days_list = options['alert_days']

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'INICIANDO ENVÍO DE ALERTAS - {today}'))
        self.stdout.write(self.style.SUCCESS(f'Días de alerta configurados: {alert_days_list}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))

        total_sent = 0

        # Procesar alertas para cada día configurado
        for days in alert_days_list:
            alert_date = today + timedelta(days=days)
            
            # Determinar tipo de alerta
            if days == 5:
                alert_type = '5_days'
            elif days == 1:
                alert_type = '1_day'
            elif days == 0:
                alert_type = 'same_day'
            else:
                alert_type = f'{days}_days'
            
            self.stdout.write(self.style.WARNING(f'\n--- Procesando alertas para {days} día(s) antes (vencen el {alert_date}) ---'))
            
            # Enviar alertas de obligaciones
            total_sent += self._send_obligation_alerts(alert_date, alert_type, days)
            
            # Enviar alertas de rentas
            total_sent += self._send_rental_alerts(alert_date, alert_type, days)
            
            # Enviar recordatorios de pagos pendientes
            total_sent += self._send_payment_reminders(alert_date, alert_type, days)

        # Resumen final
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'TOTAL: {total_sent} correos enviados'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))

    def _send_obligation_alerts(self, alert_date, alert_type, days):
        """Envía alertas de obligaciones que vencen en la fecha especificada"""
        self.stdout.write(self.style.WARNING(f'\n[1] Obligaciones que vencen el {alert_date}...'))
        
        obligations = Obligation.objects.filter(
            due_date=alert_date,
        ).select_related('property', 'obligation_type')

        sent_count = 0
        content_type = ContentType.objects.get_for_model(Obligation)

        for obligation in obligations:
            # Verificar si ya se envió esta alerta
            already_sent = AlertSent.objects.filter(
                content_type=content_type,
                object_id=obligation.id,
                alert_type=alert_type
            ).exists()

            if already_sent:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⊘ Ya enviada: {obligation.entity_name} (alerta de {days} día(s))'
                    )
                )
                continue

            # Verificar si tiene pagos suficientes
            total_paid = sum(
                payment.amount for payment in obligation.payments.all()
            )
            
            # Solo alertar si no está completamente pagada
            if total_paid < obligation.amount:
                try:
                    # Las alertas de obligaciones SIEMPRE van al admin
                    admin_emails = os.getenv('ADMIN_EMAILS', '').split(',')
                    admin_emails = [email.strip() for email in admin_emails if email.strip()]
                    
                    if not admin_emails:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ No se pudo enviar: {obligation.entity_name} (ADMIN_EMAILS no configurado en .env)'
                            )
                        )
                        continue
                    
                    # Enviar alerta a todos los admins configurados
                    emails_sent = []
                    for admin_email in admin_emails:
                        send_obligation_alert(obligation, admin_email, days)
                        emails_sent.append(admin_email)
                    
                    # Registrar alerta enviada (solo una vez, aunque se envíe a múltiples admins)
                    AlertSent.objects.create(
                        content_type=content_type,
                        object_id=obligation.id,
                        alert_type=alert_type
                    )
                    
                    sent_count += 1
                    recipients = ', '.join(emails_sent)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Alerta enviada: {obligation.entity_name} -> {recipients}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error enviando alerta: {obligation.entity_name} - {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Obligaciones: {sent_count} alertas enviadas de {obligations.count()} encontradas')
        )
        
        return sent_count

    def _send_rental_alerts(self, alert_date, alert_type, days):
        """Envía alertas de rentas que vencen en la fecha especificada"""
        self.stdout.write(self.style.WARNING(f'\n[2] Rentas que vencen el {alert_date}...'))
        
        rentals = Rental.objects.filter(
            check_out=alert_date,
            status='occupied'
        ).select_related('tenant', 'property')

        sent_count = 0
        content_type = ContentType.objects.get_for_model(Rental)

        for rental in rentals:
            # Verificar si ya se envió esta alerta
            already_sent = AlertSent.objects.filter(
                content_type=content_type,
                object_id=rental.id,
                alert_type=alert_type
            ).exists()

            if already_sent:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⊘ Ya enviada: {rental.property.name} (alerta de {days} día(s))'
                    )
                )
                continue

            try:
                if rental.tenant and rental.tenant.email:
                    send_rental_due_alert(rental, rental.tenant.email, days)
                    
                    # Registrar alerta enviada
                    AlertSent.objects.create(
                        content_type=content_type,
                        object_id=rental.id,
                        alert_type=alert_type
                    )
                    
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Alerta enviada: {rental.property.name} -> {rental.tenant.email}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ No se pudo enviar: {rental.property.name} (sin tenant o email)'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error enviando alerta: {rental.property.name} - {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Rentas: {sent_count} alertas enviadas de {rentals.count()} encontradas')
        )
        
        return sent_count

    def _send_payment_reminders(self, alert_date, alert_type, days):
        """Envía recordatorios de pagos de renta pendientes"""
        self.stdout.write(self.style.WARNING(f'\n[3] Pagos de renta pendientes (vencen el {alert_date})...'))
        
        # Rentas que vencen en la fecha especificada y no tienen suficientes pagos
        rentals = Rental.objects.filter(
            check_out=alert_date,
            status='occupied'
        ).select_related('tenant', 'property')

        sent_count = 0
        content_type = ContentType.objects.get_for_model(Rental)

        for rental in rentals:
            # Calcular total pagado
            total_paid = sum(
                payment.amount for payment in rental.payments.all()
            )
            
            # Si el pago es insuficiente, verificar si ya se envió este recordatorio
            if total_paid < rental.amount:
                # Usar tipo de alerta específico para pagos pendientes
                payment_alert_type = f'payment_{alert_type}'
                
                already_sent = AlertSent.objects.filter(
                    content_type=content_type,
                    object_id=rental.id,
                    alert_type=payment_alert_type
                ).exists()

                if already_sent:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊘ Ya enviado: {rental.property.name} (recordatorio de pago de {days} día(s))'
                        )
                    )
                    continue

                try:
                    if rental.tenant and rental.tenant.email:
                        send_rental_payment_reminder(rental, rental.tenant.email, total_paid, days)
                        
                        # Registrar recordatorio enviado
                        AlertSent.objects.create(
                            content_type=content_type,
                            object_id=rental.id,
                            alert_type=payment_alert_type
                        )
                        
                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Recordatorio enviado: {rental.property.name} -> {rental.tenant.email}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ No se pudo enviar: {rental.property.name} (sin tenant o email)'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error enviando recordatorio: {rental.property.name} - {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Pagos pendientes: {sent_count} recordatorios enviados de {rentals.count()} revisadas')
        )
        
        return sent_count

