"""
Utilidades para envío de correos electrónicos

Este módulo centraliza todas las funciones relacionadas con el envío de emails
en el sistema HR Properties. Incluye:
- Función genérica de envío de correos
- Alertas para obligaciones próximas a vencer
- Alertas para rentas próximas a vencer
- Recordatorios de pagos pendientes

IMPORTANTE PARA PRODUCCIÓN:
- Configurar EMAIL_BACKEND en settings.py
- Usar variables de entorno para credenciales
- Considerar servicio como SendGrid, Mailgun o Amazon SES
"""

from django.core.mail import send_mail
from django.conf import settings


def send_custom_email(subject, message, to_email, from_email=None):
    """
    Función genérica para enviar correos electrónicos
    
    Args:
        subject (str): Asunto del correo
        message (str): Cuerpo del mensaje (texto plano)
        to_email (str): Email del destinatario
        from_email (str, optional): Email del remitente. Si es None, usa DEFAULT_FROM_EMAIL
    
    Raises:
        Exception: Si hay error en el envío
    
    Example:
        send_custom_email(
            subject="Bienvenido",
            message="Gracias por registrarte",
            to_email="usuario@example.com"
        )
    """
    send_mail(
        subject,
        message,
        from_email,  # Usa el DEFAULT_FROM_EMAIL si es None
        [to_email],
        fail_silently=False,
    )


def send_obligation_alert(obligation, recipient_email, days=None):
    """
    Envía alerta de obligación próxima a vencer
    
    Args:
        obligation (Obligation): Instancia de la obligación
        recipient_email (str): Email del propietario
        days (int, optional): Días antes del vencimiento (para el mensaje)
    
    Example:
        obligation = Obligation.objects.get(id=1)
        send_obligation_alert(obligation, "owner@example.com", days=5)
    """
    subject = f"⚠️ Obligación próxima a vencer: {obligation.entity_name}"
    
    # Calcular cuántos días faltan
    from django.utils import timezone
    days_left = days if days is not None else (obligation.due_date - timezone.now().date()).days
    
    # Calcular total pagado
    total_paid = sum(payment.amount for payment in obligation.payments.all())
    remaining = obligation.amount - total_paid
    
    message = f"""
Dear owner,

Please be informed that the following obligation is approaching its due date:

📋 Obligation details:
- Type: {obligation.get_temporality_display()}
- Entity: {obligation.entity_name}
- Property: {obligation.property.name}
- Total amount: ${obligation.amount:,.2f}
- Amount paid: ${total_paid:,.2f}
- Amount remaining: ${remaining:,.2f}
- Due date: {obligation.due_date.strftime('%d/%m/%Y')}
- Days left: {days_left} day(s)

⏰ This is an  {days_left} day(s) before the due date.

Please, make sure to complete the payment before the due date.

Best regards,
HR Properties
    """.strip()
    
    send_custom_email(subject, message, recipient_email)


def send_rental_due_alert(rental, recipient_email, days=None):
    """
    Envía alerta de renta próxima a vencer al tenant
    
    Args:
        rental (Rental): Instancia de la renta
        recipient_email (str): Email del tenant
        days (int, optional): Días antes del vencimiento (para el mensaje)
    
    Example:
        rental = Rental.objects.get(id=1)
        send_rental_due_alert(rental, "tenant@example.com", days=5)
    """
    subject = f"🏠 Your rental in {rental.property.name} is about to end"
    
    from django.utils import timezone
    days_left = days if days is not None else (rental.check_out - timezone.now().date()).days
    
    message = f"""
Dear {rental.tenant.full_name if rental.tenant else 'Tenant'},

Please be informed that your rental contract is approaching its end date:

🏠 RENTAL DETAILS:
- Property: {rental.property.name}
- Rental type: {rental.get_rental_type_display()}
- Check-in date: {rental.check_in.strftime('%d/%m/%Y')}
- Check-out date: {rental.check_out.strftime('%d/%m/%Y')}
- Days left: {days_left} day(s)
- Monthly amount: ${rental.amount:,.2f}

⏰ This is an alert of {days_left} day(s) before the end date.

If you wish to renew the contract, please contact us as soon as possible.

Best regards,
HR Properties
    """.strip()
    
    send_custom_email(subject, message, recipient_email)


def send_rental_payment_reminder(rental, recipient_email, total_paid, days=None):
    """
    Envía recordatorio de pago pendiente de renta
    
    Args:
        rental (Rental): Instancia de la renta
        recipient_email (str): Email del tenant
        total_paid (Decimal): Total pagado hasta el momento
        days (int, optional): Días antes del vencimiento (para el mensaje)
    
    Example:
        rental = Rental.objects.get(id=1)
        send_rental_payment_reminder(rental, "tenant@example.com", Decimal('500.00'), days=1)
    """
    subject = f"💰 Payment reminder for {rental.property.name}"
    
    from django.utils import timezone
    days_left = days if days is not None else (rental.check_out - timezone.now().date()).days
    remaining = rental.amount - total_paid
    
    message = f"""
Dear {rental.tenant.full_name if rental.tenant else 'Tenant'},

Please be informed that you have a pending payment in your rental:

💰 PAYMENT DETAILS:
- Property: {rental.property.name}
- Total rental amount: ${rental.amount:,.2f}
- Amount paid: ${total_paid:,.2f}
- Amount remaining: ${remaining:,.2f}
- Check-out date: {rental.check_out.strftime('%d/%m/%Y')}
- Days left: {days_left} day(s)

⏰ This is a reminder of {days_left} day(s) before the due date.

Please make the pending payment as soon as possible.

For more information, contact us.

Best regards,
HR Properties
    """.strip()
    
    send_custom_email(subject, message, recipient_email)