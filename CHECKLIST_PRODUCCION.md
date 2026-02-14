# 🚀 CHECKLIST PRE-PRODUCCIÓN - HR PROPERTIES

## ✅ IMPLEMENTACIONES COMPLETADAS

### Sistema de Alertas por Email
- ✅ Comando `send_due_alerts` para alertas automáticas
- ✅ Funciones utilitarias para envío de emails
- ✅ Documentación completa en `apps/emails/views.py`
- ✅ API para envío manual de correos

---

## ⚠️ CAMBIOS CRÍTICOS ANTES DE PRODUCCIÓN

### 1. **SEGURIDAD - SECRET_KEY** (URGENTE) 🔴

**Problema actual:**
```python
# settings.py línea 28
SECRET_KEY = 'django-insecure-=j2fko_+lqf4*+^#ulxd!rvz*+(46$b*1b2&v30-sy%b@s+oxj'
```

**Solución:**
```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en .env")
```

**Crear archivo `.env`:**
```bash
SECRET_KEY=genera-una-key-super-segura-y-larga-aqui-min-50-caracteres
```

**Generar SECRET_KEY segura:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

### 2. **SEGURIDAD - DEBUG = False** 🔴

**Problema actual:**
```python
DEBUG = True
```

**Solución:**
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

**En `.env` de producción:**
```bash
DEBUG=False
```

---

### 3. **ALLOWED_HOSTS** 🔴

**Problema actual:**
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'http://localhost:5173', ...]
```

**Solución:**
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

**En `.env` de producción:**
```bash
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,api.tudominio.com
```

---

### 4. **BASE DE DATOS - PostgreSQL** 🟡

**Problema actual:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**SQLite NO es recomendado para producción** (problemas con concurrencia).

**Solución:**
```python
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'hr_properties'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}
```

**En `.env`:**
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_properties_production
DB_USER=hr_properties_user
DB_PASSWORD=password-super-seguro
DB_HOST=localhost
DB_PORT=5432
```

**Instalar:**
```bash
pip install psycopg2-binary
```

**Migrar datos:**
```bash
# Exportar de SQLite
python manage.py dumpdata > datadump.json

# Configurar PostgreSQL y crear DB
# Cargar datos
python manage.py migrate
python manage.py loaddata datadump.json
```

---

### 5. **EMAIL BACKEND - Producción** 🟡

**Problema actual:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Esto imprime emails en consola, NO los envía.

**Solución 1: Gmail (rápido pero limitado)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('GMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('GMAIL_USER')
```

**Solución 2: SendGrid (RECOMENDADO)**
```bash
pip install sendgrid django-sendgrid-v5
```

```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@tudominio.com')
```

---

### 6. **CORS - Configuración de producción** 🟡

**Problema actual:**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
```

**Solución:**
```python
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
```

**En `.env` de producción:**
```bash
CORS_ALLOWED_ORIGINS=https://app.tudominio.com,https://tudominio.com
```

---

### 7. **ARCHIVOS ESTÁTICOS Y MEDIA** 🟡

**Agregar a settings.py:**
```python
# Archivos estáticos (CSS, JS, imágenes del admin)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Archivos de usuario (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**Ejecutar antes de desplegar:**
```bash
python manage.py collectstatic
```

---

### 8. **HTTPS y SEGURIDAD** 🟡

**Agregar a settings.py (solo en producción):**
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

### 9. **LOGGING - Sistema de logs** 🟢

**Agregar a settings.py:**
```python
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

**Crear carpeta de logs:**
```bash
mkdir logs
```

---

### 10. **RATE LIMITING - Protección contra spam** 🟢

**Instalar:**
```bash
pip install django-ratelimit
```

**Ejemplo en EmailAPIView:**
```python
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

@method_decorator(ratelimit(key='ip', rate='10/h', method='POST'), name='dispatch')
class EmailAPIView(APIView):
    # ... código existente
```

---

### 11. **VALIDACIÓN DE MODELOS** 🟢

**Problema encontrado:**
En `apps/finance/models.py`, no hay validación de que la suma de pagos no exceda el monto de la obligación a nivel de modelo.

**Recomendación:**
Agregar método `clean()` en el modelo `PropertyPayment`:

```python
# apps/finance/models.py
class PropertyPayment(models.Model):
    # ... campos existentes
    
    def clean(self):
        if self.obligation_id:
            total_paid = PropertyPayment.objects.filter(
                obligation=self.obligation
            ).exclude(pk=self.pk).aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            if total_paid + self.amount > self.obligation.amount:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f'El total de pagos (${total_paid + self.amount}) excede '
                    f'el monto de la obligación (${self.obligation.amount})'
                )
```

---

### 12. **BACKUP AUTOMÁTICO** 🟢

**Crear script de backup:**
```bash
# backup_db.sh (Linux)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/hr_properties"
mkdir -p $BACKUP_DIR

# PostgreSQL
pg_dump -U hr_properties_user hr_properties_production > $BACKUP_DIR/db_$DATE.sql

# Archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Mantener solo últimos 30 días
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

**Programar con cron:**
```bash
0 2 * * * /path/to/backup_db.sh
```

---

### 13. **MONITOREO DE ERRORES** 🟢

**Opción 1: Sentry (Recomendado)**
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment='production' if not DEBUG else 'development'
)
```

---

### 14. **DOCUMENTACIÓN DE API** 🟢

**Instalar Swagger/OpenAPI:**
```bash
pip install drf-spectacular
```

```python
# settings.py
INSTALLED_APPS = [
    # ... otras apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    # ... configuración existente
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ... otras urls
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## 📋 ARCHIVO .ENV COMPLETO EJEMPLO

```bash
# ==========================================
# DJANGO
# ==========================================
SECRET_KEY=tu-secret-key-super-larga-y-segura-min-50-caracteres
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,api.tudominio.com

# ==========================================
# DATABASE (PostgreSQL)
# ==========================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_properties_production
DB_USER=hr_properties_user
DB_PASSWORD=password-super-seguro-aqui
DB_HOST=localhost
DB_PORT=5432

# ==========================================
# EMAIL (SendGrid recomendado)
# ==========================================
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# O Gmail (alternativa)
# GMAIL_USER=noreply@tudominio.com
# GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# ==========================================
# CORS
# ==========================================
CORS_ALLOWED_ORIGINS=https://app.tudominio.com,https://tudominio.com

# ==========================================
# GOOGLE OAUTH (si aplica)
# ==========================================
GOOGLE_CLIENT_ID=tu-client-id-aqui

# ==========================================
# MONITOREO (Sentry)
# ==========================================
SENTRY_DSN=https://xxxxxxxx@sentry.io/xxxxxxx

# ==========================================
# JWT
# ==========================================
JWT_ACCESS_TOKEN_LIFETIME_HOURS=1
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

---

## � DEPLOYMENT EN COOLIFY

**📖 GUÍA COMPLETA:** Ver [GUIA_DEPLOYMENT_COOLIFY.md](GUIA_DEPLOYMENT_COOLIFY.md)

### 📋 Resumen Ejecutivo

#### Comandos Automáticos (cada deploy)
```bash
pip install -r requirements.txt           # Instala dependencias
python manage.py collectstatic --noinput  # Recopila CSS/JS del admin
python manage.py migrate                  # Aplica migraciones
```

#### Comandos de Inicialización (una sola vez)
```bash
# 1. Crear superusuario
python manage.py createsuperuser

# 2. Verificar roles
python manage.py shell -c "from apps.users.models import Role; print(list(Role.objects.values_list('name', flat=True)))"

# 3. Asignar rol admin al superusuario
python manage.py shell -c "from django.contrib.auth import get_user_model; from apps.users.models import Role, UserRole; User = get_user_model(); admin = User.objects.get(email='admin@tuempresa.com'); role = Role.objects.get(name='admin'); UserRole.objects.get_or_create(user=admin, role=role)"
```

#### Configurar Alertas Automáticas

**Opción 1: Cron en el Servidor**
```bash
# Crear script
sudo nano /var/scripts/hr_alerts.sh
# Pegar contenido del script de alertas
sudo chmod +x /var/scripts/hr_alerts.sh

# Configurar cron
crontab -e
# Agregar: 0 8 * * * /var/scripts/hr_alerts.sh
```

**Opción 2: GitHub Actions**  
Ver archivo `.github/workflows/daily-alerts.yml` en la guía completa.

**Opción 3: Cron Externo (Cron-job.org)**  
URL: `https://api.tudominio.com/api/emails/trigger-alerts/?token=SECRET_TOKEN`

#### Variables de Entorno Mínimas
```bash
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=tudominio.com
DATABASE_URL=postgresql://...
GMAIL_USER=...
GMAIL_PASSWORD=...
ADMIN_EMAILS=...
CORS_ALLOWED_ORIGINS=https://...
SECRET_CRON_TOKEN=...
```

---

## �🔧 MEJORAS RECOMENDADAS PARA EL FUTURO

### 1. **Implementar sistema de balance/saldo a favor**
Como discutimos, agregar modelo `TenantPropertyBalance` para pagos adelantados.

### 2. **Notificaciones in-app**
Además de emails, agregar notificaciones dentro de la aplicación.

### 3. **Webhooks para pagos**
Integrar con pasarelas de pago (Stripe, PayPal) para automatizar registro de pagos.

### 4. **Reportes y Analytics**
Dashboard con estadísticas de pagos, rentas, obligaciones.

### 5. **Auditoría de cambios**
Modelo para registrar quién modificó qué y cuándo (django-auditlog).

### 6. **API versioning**
Preparar para futuras versiones de la API (/api/v1/, /api/v2/).

### 7. **Tests automatizados**
Agregar tests unitarios e integración (pytest-django).

### 8. **CI/CD Pipeline**
GitHub Actions o GitLab CI para despliegue automático.

---

## � DESPLIEGUE EN COOLIFY (SIN DOCKER)

### 📦 **COMANDOS BUILD - EN ORDEN**

Estos comandos se ejecutan **después** de hacer pull del código en producción:

```bash
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Recolectar archivos estáticos (CSS, JS, imágenes)
python manage.py collectstatic --noinput

# 3. Ejecutar migraciones de base de datos
python manage.py migrate

# 4. Verificar tipos de obligación y métodos de pago (opcional)
# Las migraciones ya crean estos datos automáticamente
# Solo ejecuta estos si necesitas verificar manualmente:
---

## ✅ CHECKLIST FINAL

Antes de lanzar a producción:

- [ ] SECRET_KEY en variable de entorno
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] Base de datos PostgreSQL configurada
- [ ] EMAIL_BACKEND de producción (SendGrid o Gmail)
- [ ] CORS configurado para dominio de producción
- [ ] HTTPS habilitado (certificado SSL)
- [ ] Archivos estáticos recolectados (`collectstatic`)
- [ ] Sistema de logs configurado
- [ ] Backups automáticos programados
- [ ] Rate limiting en endpoints críticos
- [ ] Monitoreo de errores (Sentry)
- [ ] Documentación de API
- [ ] Tests de carga (stress testing)
- [ ] Plan de rollback en caso de errores
- [ ] Migración de datos de SQLite a PostgreSQL
- [ ] Variables de entorno documentadas
- [ ] .env.example creado (sin valores reales)

---

## 📞 CONTACTO Y SOPORTE

Si necesitas ayuda con alguno de estos puntos, no dudes en consultar la documentación oficial:
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- SendGrid: https://docs.sendgrid.com/
- PostgreSQL: https://www.postgresql.org/docs/

---

**Fecha de revisión:** Febrero 2026  
**Versión:** 1.0
