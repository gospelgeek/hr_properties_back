"""
========================================
VISTAS DE EMAILS - HR PROPERTIES
========================================

Este módulo maneja el envío de correos electrónicos del sistema.

FUNCIONALIDADES:
1. Envío manual de correos (EmailAPIView)
2. Alertas automáticas mediante comando Django (send_due_alerts)

========================================
📧 EMAIL API VIEW
========================================

ENDPOINT: POST /api/emails/send-email/
AUTENTICACIÓN: Requiere JWT Token
MÉTODO: POST

DESCRIPCIÓN:
    Vista para enviar correos electrónicos manualmente desde la API.
    Útil para envíos personalizados, notificaciones específicas o pruebas.

PARÁMETROS (JSON Body):
    {
        "to_email": "destinatario@example.com",  # REQUERIDO
        "subject": "Asunto del correo",          # REQUERIDO
        "message": "Cuerpo del mensaje"          # REQUERIDO
    }

EJEMPLO DE USO (JavaScript/Fetch):
    ```javascript
    const response = await fetch('http://localhost:8000/api/emails/send-email/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_JWT_TOKEN'
        },
        body: JSON.stringify({
            to_email: 'tenant@example.com',
            subject: 'Recordatorio de pago',
            message: 'Estimado inquilino, le recordamos...'
        })
    });
    const data = await response.json();
    console.log(data.message);
    ```

EJEMPLO DE USO (Python/requests):
    ```python
    import requests
    
    url = 'http://localhost:8000/api/emails/send-email/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'
    }
    data = {
        'to_email': 'tenant@example.com',
        'subject': 'Recordatorio de pago',
        'message': 'Estimado inquilino, le recordamos...'
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    ```

EJEMPLO DE USO (cURL):
    ```bash
    curl -X POST http://localhost:8000/api/emails/send-email/ \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
      -d '{
        "to_email": "tenant@example.com",
        "subject": "Recordatorio de pago",
        "message": "Estimado inquilino, le recordamos..."
      }'
    ```

RESPUESTAS:
    Success (200):
        {
            "message": "Correo Enviado con Exito"
        }
    
    Error - Campos faltantes (400):
        {
            "message": "Faltan campos requeridos"
        }
    
    Error - Fallo en envío (400):
        {
            "message": "Descripción del error"
        }

========================================
🤖 ALERTAS AUTOMÁTICAS
========================================

COMANDO: python manage.py send_due_alerts

DESCRIPCIÓN:
    Envía automáticamente alertas por correo electrónico para:
    1. Obligaciones próximas a vencer (a propietarios)
    2. Rentas próximas a vencer (a tenants)
    3. Pagos de renta pendientes (a tenants)

PARÁMETROS OPCIONALES:
    --days N    # Días de anticipación (default: 5)

EJEMPLO DE USO:
    # Alerta 5 días antes (default)
    python manage.py send_due_alerts
    
    # Alerta 7 días antes
    python manage.py send_due_alerts --days 7

PROGRAMACIÓN AUTOMÁTICA:
    Ver documentación en:
    apps/emails/management/commands/send_due_alerts.py

========================================
⚙️ CONFIGURACIÓN
========================================

DESARROLLO (settings.py):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    # Los emails se imprimen en la consola para pruebas

PRODUCCIÓN (settings.py):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('GMAIL_USER')
    EMAIL_HOST_PASSWORD = os.getenv('GMAIL_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('GMAIL_USER')

    # O usar servicios profesionales:
    # - SendGrid (recomendado para producción)
    # - Mailgun
    # - Amazon SES
    # - Postmark

========================================
📚 FUNCIONES UTILITARIAS
========================================

Ubicación: apps/emails/utils.py

Funciones disponibles:
1. send_custom_email(subject, message, to_email, from_email=None)
   - Envío genérico de correos
   
2. send_obligation_alert(obligation, recipient_email)
   - Alerta de obligación próxima a vencer
   
3. send_rental_due_alert(rental, recipient_email)
   - Alerta de renta próxima a vencer
   
4. send_rental_payment_reminder(rental, recipient_email, total_paid)
   - Recordatorio de pago pendiente

EJEMPLO DE USO EN CÓDIGO:
    ```python
    from apps.emails.utils import send_custom_email, send_rental_due_alert
    
    # Envío manual
    send_custom_email(
        subject="Bienvenido",
        message="Gracias por registrarte",
        to_email="user@example.com"
    )
    
    # Alerta de renta
    rental = Rental.objects.get(id=1)
    send_rental_due_alert(rental, rental.tenant.email)
    ```

========================================
🔒 SEGURIDAD
========================================

- Esta vista requiere autenticación JWT
- Los correos solo se envían a direcciones validadas
- No usar credenciales hardcodeadas (usar variables de entorno)
- En producción, limitar rate de envío para evitar spam
- Considerar implementar cola de mensajes (Celery) para envíos masivos

========================================
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import send_custom_email


class EmailAPIView(APIView):
    """
    Vista API para envío manual de correos electrónicos
    
    Ver documentación completa al inicio de este archivo.
    """
    
    def post(self, request):
        """
        Envía un correo electrónico
        
        Body params:
            - to_email: Email del destinatario (requerido)
            - subject: Asunto del correo (requerido)
            - message: Cuerpo del mensaje (requerido)
        
        Returns:
            200: Correo enviado exitosamente
            400: Error en validación o envío
        """
        try:
            # Obtener datos del request
            to_email = request.data.get('to_email')
            subject = request.data.get('subject')
            message = request.data.get('message')
            
            # Validar campos requeridos
            if not to_email or not subject or not message:
                return Response(
                    {'message': 'Faltan campos requeridos (to_email, subject, message)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Enviar correo
            send_custom_email(subject, message, to_email)
            
            return Response(
                {'message': 'Correo Enviado con Exito'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            error_message = str(e)
            return Response(
                {'message': f'Error al enviar correo: {error_message}'},
                status=status.HTTP_400_BAD_REQUEST
            )
