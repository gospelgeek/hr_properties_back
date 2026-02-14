# 📧 App de Emails - HR Properties

Sistema de envío de correos electrónicos para alertas automáticas y notificaciones manuales.

## 🎯 Funcionalidades

1. **Envío manual de correos** - API REST para enviar emails personalizados
2. **Alertas automáticas** - Comando para enviar notificaciones programadas:
   - Obligaciones próximas a vencer
   - Rentas próximas a vencer
   - Pagos de renta pendientes

---

## 📁 Estructura

```
apps/emails/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py              # API para envío manual
├── utils.py              # Funciones de envío de correos
└── management/
    └── commands/
        └── send_due_alerts.py  # Comando de alertas automáticas
```

---

## 🚀 Uso Rápido

### 1. Envío Manual (API)

**Endpoint:** `POST /api/emails/send-email/`

**Request:**
```json
{
  "to_email": "usuario@example.com",
  "subject": "Asunto del correo",
  "message": "Contenido del mensaje"
}
```

**Response (Success):**
```json
{
  "message": "Correo Enviado con Exito"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/emails/send-email/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test",
    "message": "Hello World"
  }'
```

### 2. Alertas Automáticas (Comando)

**Ejecutar manualmente:**
```bash
# Alertar 5 días antes (default)
python manage.py send_due_alerts

# Alertar 7 días antes
python manage.py send_due_alerts --days 7
```

**Programar automáticamente:**

#### Windows (Task Scheduler)
1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Configurar:
   - **Trigger:** Diario a las 8:00 AM
   - **Acción:** Iniciar programa
   - **Programa:** `C:\ruta\venv\Scripts\python.exe`
   - **Argumentos:** `manage.py send_due_alerts`
   - **Comenzar en:** `C:\ruta\proyecto`

#### Linux (Cron)
```bash
crontab -e

# Ejecutar todos los días a las 8:00 AM
0 8 * * * cd /ruta/proyecto && /ruta/venv/bin/python manage.py send_due_alerts
```

---

## 📝 Funciones Utilitarias

### `send_custom_email()`
```python
from apps.emails.utils import send_custom_email

send_custom_email(
    subject="Bienvenido",
    message="Gracias por registrarte",
    to_email="usuario@example.com"
)
```

### `send_obligation_alert()`
```python
from apps.emails.utils import send_obligation_alert

obligation = Obligation.objects.get(id=1)
send_obligation_alert(obligation, "owner@example.com")
```

### `send_rental_due_alert()`
```python
from apps.emails.utils import send_rental_due_alert

rental = Rental.objects.get(id=1)
send_rental_due_alert(rental, rental.tenant.email)
```

### `send_rental_payment_reminder()`
```python
from apps.emails.utils import send_rental_payment_reminder

rental = Rental.objects.get(id=1)
total_paid = Decimal('500.00')
send_rental_payment_reminder(rental, rental.tenant.email, total_paid)
```

---

## ⚙️ Configuración

### Desarrollo (Emails en consola)

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los emails se imprimirán en la consola para pruebas.

### Producción (Envío real)

#### Opción 1: Gmail
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('GMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('GMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('GMAIL_USER')
```

**Configurar App Password en Gmail:**
1. Ir a https://myaccount.google.com/
2. Seguridad → Verificación en dos pasos (activar)
3. Seguridad → Contraseñas de aplicaciones
4. Generar contraseña para "Correo"
5. Usar esa contraseña en `.env`

#### Opción 2: SendGrid (Recomendado)
```bash
pip install sendgrid django-sendgrid-v5
```

```python
# settings.py
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
```

**Ventajas de SendGrid:**
- 100 emails/día gratis
- Mejor deliverability
- Analytics incluidos
- Templates HTML

---

## 📋 Variables de Entorno

```bash
# .env
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# Gmail
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxx
```

---

## 🔍 Tipos de Alertas

### 1. Obligaciones Próximas a Vencer
- **Destinatario:** Propietario de la propiedad
- **Cuándo:** X días antes del vencimiento
- **Contenido:**
  - Tipo de obligación
  - Entidad
  - Propiedad
  - Monto total y pendiente
  - Fecha de vencimiento
  - Días restantes

### 2. Rentas Próximas a Vencer
- **Destinatario:** Tenant (inquilino)
- **Cuándo:** X días antes de la fecha de salida
- **Contenido:**
  - Propiedad
  - Tipo de renta
  - Fechas de entrada/salida
  - Días restantes
  - Monto mensual

### 3. Pagos Pendientes
- **Destinatario:** Tenant (inquilino)
- **Cuándo:** Rentas con pagos incompletos
- **Contenido:**
  - Propiedad
  - Monto total y pagado
  - Monto pendiente
  - Fecha de salida

---

## 📱 Ejemplos de Uso en Código

### En una vista
```python
from apps.emails.utils import send_custom_email

class MyView(APIView):
    def post(self, request):
        # ... lógica de negocio
        
        send_custom_email(
            subject="Confirmación de registro",
            message=f"Bienvenido {user.name}",
            to_email=user.email
        )
        
        return Response({"message": "OK"})
```

### En una señal
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.emails.utils import send_custom_email

@receiver(post_save, sender=Rental)
def rental_created(sender, instance, created, **kwargs):
    if created:
        send_custom_email(
            subject="Nueva renta creada",
            message=f"Se creó una renta en {instance.property.name}",
            to_email=instance.tenant.email
        )
```

---

## 🐛 Troubleshooting

### Error: "SMTPAuthenticationError"
- Verificar credenciales en `.env`
- Si usas Gmail, generar App Password
- Verificar que 2FA esté habilitado

### Los emails no llegan
- Revisar carpeta de spam
- Verificar que DEFAULT_FROM_EMAIL sea válido
- Revisar logs de Django

### Error: "Connection refused"
- Verificar EMAIL_HOST y EMAIL_PORT
- Verificar firewall

---

## 📚 Documentación Adicional

- Ver [views.py](views.py) para documentación completa de la API
- Ver [CHECKLIST_PRODUCCION.md](../../CHECKLIST_PRODUCCION.md) para configuración de producción
- Ver [PRODUCCION_EMAIL_CONFIG.md](../../PRODUCCION_EMAIL_CONFIG.md) para ejemplos de configuración

---

## 🔒 Seguridad

- ✅ Requiere autenticación JWT
- ✅ No expone credenciales en código
- ✅ Usa variables de entorno
- ⚠️ Considerar rate limiting en producción
- ⚠️ Validar direcciones de email

---

**Última actualización:** Febrero 2026
