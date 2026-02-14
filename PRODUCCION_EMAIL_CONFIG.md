"""
========================================
CONFIGURACIÓN DE PRODUCCIÓN - HR PROPERTIES
========================================

Este archivo contiene ejemplos de configuración para producción.
NO commitear este archivo con valores reales.

========================================
1. VARIABLES DE ENTORNO (.env)
========================================

Crear archivo .env en la raíz del proyecto:

# Django
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos (PostgreSQL recomendado)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_properties_db
DB_USER=hr_properties_user
DB_PASSWORD=password-seguro-aqui
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail)
GMAIL_USER=noreply@tudominio.com
GMAIL_PASSWORD=tu-app-password-aqui
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# Email (SendGrid - RECOMENDADO)
SENDGRID_API_KEY=tu-api-key-aqui
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# CORS
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com

========================================
2. SETTINGS.PY - PRODUCCIÓN
========================================

import os
from dotenv import load_dotenv

load_dotenv()

# SEGURIDAD
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Base de datos PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Email - Opción 1: Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('GMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('GMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Email - Opción 2: SendGrid (RECOMENDADO)
# pip install sendgrid
# EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Seguridad adicional
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Archivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

========================================
3. GMAIL - CONFIGURACIÓN APP PASSWORD
========================================

1. Ir a Google Account: https://myaccount.google.com/
2. Seguridad -> Verificación en dos pasos (activar)
3. Seguridad -> Contraseñas de aplicaciones
4. Generar contraseña para "Correo"
5. Usar esa contraseña en GMAIL_PASSWORD

========================================
4. SENDGRID - CONFIGURACIÓN (RECOMENDADO)
========================================

1. Crear cuenta en https://sendgrid.com/ (100 emails/día gratis)
2. Crear API Key en Settings -> API Keys
3. Verificar dominio/email en Sender Authentication
4. Instalar: pip install sendgrid django-sendgrid-v5
5. Configurar en settings.py como se muestra arriba

VENTAJAS:
- Mejor deliverability que Gmail
- Analytics y tracking
- Templates HTML profesionales
- No requiere autenticación de 2 factores

========================================
5. PROGRAMACIÓN DE ALERTAS
========================================

WINDOWS (Task Scheduler):
1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Nombre: "HR Properties - Alertas Diarias"
4. Trigger: Diario a las 8:00 AM
5. Acción: Iniciar programa
   - Programa: C:\\ruta\\al\\venv\\Scripts\\python.exe
   - Argumentos: manage.py send_due_alerts
   - Comenzar en: C:\\ruta\\al\\proyecto
6. Guardar con usuario que tenga permisos

LINUX (Cron):
crontab -e

# Ejecutar todos los días a las 8:00 AM
0 8 * * * cd /ruta/al/proyecto && /ruta/al/venv/bin/python manage.py send_due_alerts >> /var/log/hr_alerts.log 2>&1

========================================
6. LOGS Y MONITOREO
========================================

# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

========================================
7. CELERY (Opcional - Para envíos masivos)
========================================

Si necesitas enviar muchos emails o procesar tareas en background:

pip install celery redis

# celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_properties.settings')
app = Celery('hr_properties')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# tasks.py
from celery import shared_task
from apps.emails.utils import send_custom_email

@shared_task
def send_email_task(subject, message, to_email):
    send_custom_email(subject, message, to_email)

========================================
"""
