# 🚀 GUÍA COMPLETA: DEPLOYMENT EN COOLIFY (LINUX - SIN DOCKER)

**Fecha:** Febrero 2026  
**Plataforma:** Coolify (Linux Ubuntu/Debian)  
**Base de Datos:** PostgreSQL  
**Servidor Web:** Gunicorn + Nginx (gestionado por Coolify)

---

## 📋 ÍNDICE

1. [Preparación del Proyecto](#paso-0-preparación-del-proyecto)
2. [Configurar Coolify](#paso-1-configurar-coolify)
3. [Primer Deployment](#paso-2-primer-deployment)
4. [Comandos de Inicialización](#paso-3-comandos-de-inicialización)
5. [Comandos en Cada Deploy](#paso-4-comandos-en-cada-deploy)
6. [Configurar Alertas Automáticas](#paso-5-alertas-automáticas)
7. [GitHub Actions para Alertas](#paso-6-github-actions)
8. [Troubleshooting](#troubleshooting)

---

## 📦 PASO 0: PREPARACIÓN DEL PROYECTO (ANTES DE DEPLOYAR)

### 1. Actualizar `requirements.txt`

Tu `requirements.txt` **DEBE** incluir:

```txt
# Core Django
Django>=5.0,<6.0
djangorestframework>=3.14.0

# Authentication
djangorestframework-simplejwt>=5.3.0
google-auth>=2.23.0
dj-rest-auth>=5.0.0

# Utilities
django-filter>=24.2
python-decouple>=3.8
python-dotenv>=1.0.0
Pillow>=10.0.0
django-cors-headers>=4.3.0

# Database (OBLIGATORIO para producción)
psycopg2-binary>=2.9.0

# Production (OBLIGATORIO)
gunicorn>=21.2.0      # Servidor WSGI
whitenoise>=6.6.0     # Servir archivos estáticos

# Email
django-sendgrid-v5>=1.2.0  # Opcional pero recomendado

# Development
coverage>=7.0.0
```

**📝 Ejecutar localmente:**
```bash
pip install -r requirements.txt
pip freeze > requirements.txt  # Generar con versiones exactas
git add requirements.txt
git commit -m "Update requirements for production"
git push
```

---

### 2. Verificar `.gitignore`

Asegúrate de que **NO SUBES** estos archivos a Git:

```gitignore
# Python
*.pyc
__pycache__/
*.egg-info

# Django
db.sqlite3
*.log
media/              # ⚠️ MUY IMPORTANTE
staticfiles/

# Environment
.env                # ⚠️ CRÍTICO
venv/
env/

# IDE
.vscode/
.idea/
```

**⚠️ Si `media/` ya está en Git:**
```bash
git rm -r --cached media/
echo "media/" >> .gitignore
git add .gitignore
git commit -m "Remove media folder from version control"
git push
```

---

### 3. Crear `.env.example` (Template)

Crea un archivo `.env.example` con valores de ejemplo (SIN datos reales):

```bash
# Django Core
SECRET_KEY=cambiar-por-secret-key-segura-50-caracteres
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Database PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_properties
DB_USER=hr_properties_user
DB_PASSWORD=cambiar-password-seguro
DB_HOST=localhost
DB_PORT=5432

# Email Gmail
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password-16-caracteres

# Admin Emails
ADMIN_EMAILS=admin@empresa.com

# CORS
CORS_ALLOWED_ORIGINS=https://app.tudominio.com

# Google OAuth
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret

# Cron Security
SECRET_CRON_TOKEN=generar-token-64-caracteres
```

```bash
git add .env.example
git commit -m "Add .env.example template"
git push
```

---

## 🔧 PASO 1: CONFIGURAR COOLIFY

### 1.1 Crear Aplicación

1. Accede a Coolify: `https://tu-coolify.com`
2. Click en **New Resource** → **Application**
3. **Source:** Public Repository (Git)
4. Pega la URL de tu repositorio: `https://github.com/tu-usuario/hr-properties`
5. Selecciona rama: `main`
6. Click **Continue**

---

### 1.2 Configurar Build Settings

**Build Pack:** Python (se detecta automáticamente)

**Install Command:**
```bash
pip install -r requirements.txt
```

**Build Command:**
```bash
python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```bash
gunicorn hr_properties.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile -
```

**Port:** `8000`

**📝 EXPLICACIÓN DE CADA COMANDO:**

| Comando | ¿Cuándo se ejecuta? | ¿Qué hace? |
|---------|---------------------|------------|
| `pip install -r requirements.txt` | Cada deploy | Instala todas las dependencias Python |
| `python manage.py collectstatic --noinput` | Cada deploy | Recopila archivos CSS/JS del admin de Django |
| `python manage.py migrate` | Cada deploy | Aplica migraciones de base de datos nuevas |
| `gunicorn ...` | Al iniciar la app | Inicia el servidor WSGI de producción |

**Parámetros de Gunicorn:**
- `--workers 3`: 3 procesos concurrentes (ajusta según RAM: 2×CPU cores + 1)
- `--timeout 120`: Timeout de 120seg para requests largos
- `--access-logfile -`: Logs de acceso a stdout
- `--error-logfile -`: Logs de errores a stdout

---

### 1.3 Crear Base de Datos PostgreSQL

**Opción A: PostgreSQL de Coolify (RECOMENDADA)**

1. En Coolify: **New Resource** → **Database** → **PostgreSQL 16**
2. Nombre: `hr-properties-db`
3. Click **Deploy**
4. Coolify generará automáticamente:
   - `POSTGRESQL_URL`: `postgresql://user:pass@host:5432/dbname`
   
5. **Copiar la `POSTGRESQL_URL`** para usarla en variables de entorno

**Opción B: PostgreSQL Externo (DigitalOcean, AWS RDS)**

Necesitarás configurar manualmente:
- `DB_HOST`: IP o hostname
- `DB_PORT`: 5432 (default)
- `DB_NAME`: `hr_properties`
- `DB_USER`: usuario
- `DB_PASSWORD`: contraseña

---

### 1.4 Configurar Variables de Entorno

En Coolify: **Application** → **Environment Variables** → **Add**

Agrega TODAS estas variables (ajusta los valores):

```bash
# ══════════════════════════════════════
# DJANGO CORE
# ══════════════════════════════════════
SECRET_KEY=django-insecure-TU-SECRET-KEY-AQUI-MIN-50-CARACTERES
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,api.tudominio.com

# ══════════════════════════════════════
# DATABASE (Opción A: usando DATABASE_URL de Coolify)
# ══════════════════════════════════════
DATABASE_URL=postgresql://user:password@postgres-host:5432/hr_properties

# ══════════════════════════════════════
# EMAIL - GMAIL
# ══════════════════════════════════════
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
GMAIL_USER=hrpropertiessystem@gmail.com
GMAIL_PASSWORD=qyih spoe pntl zhre
DEFAULT_FROM_EMAIL=hrpropertiessystem@gmail.com

# ══════════════════════════════════════
# ADMIN EMAILS (para alertas de obligaciones)
# ══════════════════════════════════════
ADMIN_EMAILS=hrpropertiessystem@gmail.com,admin2@empresa.com

# ══════════════════════════════════════
# CORS
# ══════════════════════════════════════
CORS_ALLOWED_ORIGINS=https://app.tudominio.com,https://tudominio.com

# ══════════════════════════════════════
# GOOGLE OAUTH (opcional)
# ══════════════════════════════════════


# ══════════════════════════════════════
# CRON SECURITY TOKEN (para alertas automáticas)
# ══════════════════════════════════════
SECRET_CRON_TOKEN=generar-token-aleatorio-64-caracteres-aqui

# ══════════════════════════════════════
# STATIC/MEDIA FILES
# ══════════════════════════════════════
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=/app/media/
```

**🔐 Cómo generar valores seguros:**

**SECRET_KEY:**
```bash
# Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**SECRET_CRON_TOKEN:**
```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Gmail App Password:**
1. https://myaccount.google.com/security
2. Activa verificación en 2 pasos
3. Busca "Contraseñas de aplicaciones"
4. Genera una para "Mail"
5. Usa esa contraseña de 16 caracteres

---

### 1.5 Configurar Dominio y SSL

1. En Coolify: **Application** → **Domains**
2. Agrega: `api.tudominio.com` (o el dominio que uses)
3. Coolify configurará automáticamente:
   - SSL con Let's Encrypt
   - Certificado HTTPS
   - Redirección HTTP → HTTPS

**DNS:** Asegúrate de que tu dominio apunta a la IP del servidor Coolify:
```
A    api.tudominio.com    →    IP_DEL_SERVIDOR
```

---

## 🚀 PASO 2: PRIMER DEPLOYMENT

### 2.1 Deployar la Aplicación

En Coolify:
1. Click en **Deploy**
2. Espera 2-5 minutos

Coolify ejecutará automáticamente:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn hr_properties.wsgi:application ...
```

---

### 2.2 Verificar Deploy Exitoso

**Revisar logs:**
- Coolify → Application → **Build Logs**
- Debe mostrar: `✓ Deployment successful`

**Probar endpoints:**
```bash
# API debe responder
curl https://api.tudominio.com/api/

# Admin debe cargar (sin CSS es normal en primer deploy)
curl https://api.tudominio.com/admin/
```

Si todo está OK, continúa al Paso 3.

---

## 🔧 PASO 3: COMANDOS DE INICIALIZACIÓN (EJECUTAR UNA SOLA VEZ)

### ⚠️ IMPORTANTE  
Estos comandos se ejecutan **UNA SOLA VEZ** después del primer deploy exitoso.  
**NO ejecutarlos en cada deploy.**

---

### 3.1 Acceder al Servidor

**Opción 1: Consola de Coolify**
- Coolify → Application → **Console** (icono de terminal)

**Opción 2: SSH**
```bash
ssh usuario@IP_DEL_SERVIDOR
cd /ruta/de/la/app  # Coolify te dirá la ruta exacta
```

---

### 3.2 Activar Entorno Virtual

```bash
# Coolify crea un venv automáticamente
source venv/bin/activate
```

Tu prompt cambiará a:
```bash
(venv) usuario@servidor:/ruta/de/la/app$
```

---

### 3.3 Crear Superusuario (Admin Principal)

```bash
python manage.py createsuperuser
```

Te pedirá:
```
Email: admin@tuempresa.com
Name: Administrador Principal
Password: ********** (elige una contraseña segura)
Password (again): **********
```

✅ **Superusuario creado**

**📝 Cuándo ejecutar:**
- ✅ Una sola vez, después del primer deploy
- ❌ NO ejecutar en cada deploy

---

### 3.4 Verificar y Crear Roles

**Verificar si existen:**
```bash
python manage.py shell -c "from apps.users.models import Role; print('Roles:', list(Role.objects.values_list('name', flat=True)))"
```

Debería mostrar:
```
Roles: ['admin', 'cliente']
```

**Si NO existen, créalos:**
```bash
python manage.py shell
```

Dentro del shell:
```python
from apps.users.models import Role

# Crear roles
admin_role, created = Role.objects.get_or_create(name='admin')
print(f"{'✅ Creado' if created else 'ℹ️  Ya existe'}: rol admin")

cliente_role, created = Role.objects.get_or_create(name='cliente')
print(f"{'✅ Creado' if created else 'ℹ️  Ya existe'}: rol cliente")

# Salir
exit()
```

**Alternativa rápida (una línea):**
```bash
python manage.py shell -c "from apps.users.models import Role; Role.objects.get_or_create(name='admin'); Role.objects.get_or_create(name='cliente'); print('✅ Roles verificados')"
```

**📝 Cuándo ejecutar:**
- ✅ Una sola vez, para verificar
- ℹ️  Las migraciones ya deben haberlos creado automáticamente

---

### 3.5 Asignar Rol Admin al Superusuario

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from apps.users.models import Role, UserRole

User = get_user_model()

# Obtener el superusuario (ajusta el email si es diferente)
admin_user = User.objects.get(email='admin@tuempresa.com')

# Asignar rol admin
admin_role = Role.objects.get(name='admin')
user_role, created = UserRole.objects.get_or_create(user=admin_user, role=admin_role)

if created:
    print(f"✅ Rol 'admin' asignado a {admin_user.email}")
else:
    print(f"ℹ️  {admin_user.email} ya tiene rol 'admin'")

exit()
```

**Alternativa rápida:**
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; from apps.users.models import Role, UserRole; User = get_user_model(); admin = User.objects.get(email='admin@tuempresa.com'); role = Role.objects.get(name='admin'); UserRole.objects.get_or_create(user=admin, role=role); print('✅ Rol asignado')"
```

**📝 Cuándo ejecutar:**
- ✅ Una sola vez, después de crear el superusuario
- ⚠️ **MUY IMPORTANTE:** Sin este paso, el admin NO tendrá permisos correctos en la API

---

### 3.6 Verificar Tipos de Obligación y Métodos de Pago

Estos se crean automáticamente con las migraciones, pero verifica:

```bash
python manage.py shell -c "from apps.finance.models import ObligationType, PaymentMethod; print('✅ Obligation Types:', list(ObligationType.objects.values_list('name', flat=True))); print('✅ Payment Methods:', list(PaymentMethod.objects.values_list('name', flat=True)))"
```

**Resultado esperado:**
```
✅ Obligation Types: ['tax', 'insurance', 'fee']
✅ Payment Methods: ['cash', 'transfer', 'check', 'card', 'zelle']
```

**📝 Cuándo ejecutar:**
- ✅ Opcional, solo para verificar
- ℹ️  Las migraciones ya los crean automáticamente

---

### 📋 RESUMEN DE COMANDOS DE INICIALIZACIÓN

| Comando | ¿Cuántas veces? | ¿Cuándo? |
|---------|-----------------|----------|
| `createsuperuser` | **1 vez** | Después del primer deploy |
| Crear roles | **1 vez** | Después del primer deploy (opcional si migraciones existen) |
| Asignar rol admin | **1 vez** | Después de crear superusuario |
| Verificar obligation types | **Opcional** | Solo para verificar |
| Verificar payment methods | **Opcional** | Solo para verificar |

---

## 🔄 PASO 4: COMANDOS QUE SE EJECUTAN EN CADA DEPLOY

Estos comandos **SE EJECUTAN AUTOMÁTICAMENTE** en cada deploy (ya están configurados en Coolify):

```bash
# 1. Instalar/actualizar dependencias
pip install -r requirements.txt

# 2. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 3. Aplicar migraciones nuevas
python manage.py migrate
```

**📝 Cuándo se ejecutan:**
- ✅ Automáticamente en cada deploy
- ✅ No necesitas ejecutarlos manualmente
- ⚠️ Si alguno falla, el deploy se detendrá (seguridad)

**❓ ¿Cuándo ejecutarlos manualmente?**
- Solo si el deploy automático falla y necesitas debuggear
- Si haces cambios directamente en el servidor (NO recomendado)

---

## ⏰ PASO 5: CONFIGURAR ALERTAS AUTOMÁTICAS

El sistema de alertas envía emails automáticamente cuando:
- Obligaciones próximas a vencer (5 días y 1 día antes)
- Rentas próximas a vencer
- Pagos pendientes

### Opción 1: Cron en el Servidor (RECOMENDADA)

#### 5.1.1 Acceder al Servidor por SSH

```bash
ssh usuario@IP_DEL_SERVIDOR
```

#### 5.1.2 Crear Script de Alertas

```bash
# Crear directorio para scripts
sudo mkdir -p /var/scripts

# Crear script (ajusta la ruta al proyecto)
sudo nano /var/scripts/hr_alerts.sh
```

Pega este contenido:
```bash
#!/bin/bash
# Script para ejecutar alertas automáticas de HR Properties

# Ruta al proyecto (AJUSTAR según tu instalación de Coolify)
PROJECT_PATH="/home/coolify/hr-properties"  # Verifica esta ruta

cd $PROJECT_PATH

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar comando de alertas
python manage.py send_due_alerts --alert-days 5 1 >> /var/log/hr_alerts.log 2>&1

# Desactivar entorno virtual
deactivate 2>/dev/null || true
```

Guarda: `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Hacer ejecutable
sudo chmod +x /var/scripts/hr_alerts.sh
```

#### 5.1.3 Configurar Cron Job

```bash
# Editar crontab
crontab -e
```

Agrega esta línea al final:
```bash
# Ejecutar alertas todos los días a las 8:00 AM
0 8 * * * /var/scripts/hr_alerts.sh
```

Guarda: `Ctrl+O`, `Enter`, `Ctrl+X`

#### 5.1.4 Verificar Cron

```bash
# Ver cron jobs configurados
crontab -l

# Ejecutar manualmente para probar
/var/scripts/hr_alerts.sh

# Ver logs
tail -f /var/log/hr_alerts.log
```

**📌 Sintaxis de Cron:**
```
┌─── minuto (0-59)
│ ┌─── hora (0-23)
│ │ ┌─── día del mes (1-31)
│ │ │ ┌─── mes (1-12)
│ │ │ │ ┌─── día de la semana (0-6, 0=Domingo)
│ │ │ │ │
* * * * * comando

Ejemplos:
0 8 * * *       → Todos los días a las 8:00 AM
0 8,20 * * *    → Diario a las 8:00 AM y 8:00 PM
0 8 * * 1       → Todos los lunes a las 8:00 AM
0 8 1 * *       → El día 1 de cada mes a las 8:00 AM
*/30 * * * *    → Cada 30 minutos
```

---

### Opción 2: Servicio de Cron Externo

Si no tienes acceso SSH al servidor, usa un servicio externo:

**Servicios recomendados:**
- **Cron-job.org** (gratis, ilimitado)
- **EasyCron** (gratis hasta 5 jobs)
- **Uptimerobot** (gratis, también monitorea uptime)

#### 5.2.1 Crear Endpoint de Trigger

Agrega en `apps/emails/views.py`:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.management import call_command
import os

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def trigger_alerts(request):
    """
    Endpoint para disparar alertas desde un servicio de cron externo
    
    Protegido con SECRET_CRON_TOKEN
    GET /api/emails/trigger-alerts/?token=TU_SECRET_TOKEN
    """
    # Verificar token de seguridad
    secret_token = os.getenv('SECRET_CRON_TOKEN', '')
    provided_token = request.GET.get('token') or request.POST.get('token')
    
    if not secret_token or provided_token != secret_token:
        return Response({'error': 'Unauthorized'}, status=403)
    
    # Ejecutar comando de alertas
    try:
        call_command('send_due_alerts', '--alert-days', '5', '1')
        return Response({
            'status': 'success',
            'message': 'Alertas enviadas correctamente'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)
```

Agrega en `apps/emails/urls.py`:
```python
from .views import trigger_alerts

urlpatterns = [
    path('trigger-alerts/', trigger_alerts, name='trigger-alerts'),
    # ... otras rutas
]
```

Commitea y haz deploy:
```bash
git add apps/emails/views.py apps/emails/urls.py
git commit -m "Add trigger endpoint for external cron"
git push
```

#### 5.2.2 Configurar en Cron-job.org

1. Ve a https://cron-job.org/
2. Regístrate gratis
3. Click **Create cronjob**
4. **Title:** HR Properties Alerts
5. **URL:** `https://api.tudominio.com/api/emails/trigger-alerts/?token=TU_SECRET_TOKEN`
6. **Schedule:** Daily at 08:00
7. **Timezone:** America/Bogota
8. Click **Create**

---

## 🤖 PASO 6: GITHUB ACTIONS PARA ALERTAS (OPCIONAL)

Si prefieres usar GitHub Actions para ejecutar las alertas:

### 6.1 Crear Workflow

Crea `.github/workflows/daily-alerts.yml`:

```yaml
name: Enviar Alertas Diarias

on:
  schedule:
    # Ejecutar todos los días a las 8:00 AM Colombia (13:00 UTC)
    # GitHub Actions usa UTC
    - cron: '0 13 * * *'
  workflow_dispatch:  # Permite ejecución manual

jobs:
  send-alerts:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger alerts endpoint
        run: |
          RESPONSE=$(curl -s -w "\n%{http_code}" "${{ secrets.ALERTS_ENDPOINT_URL }}?token=${{ secrets.CRON_TOKEN }}")
          HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
          BODY=$(echo "$RESPONSE" | head -n-1)
          
          echo "HTTP Code: $HTTP_CODE"
          echo "Response: $BODY"
          
          if [ "$HTTP_CODE" != "200" ]; then
            echo "Error: Failed to send alerts"
            exit 1
          fi
        
      - name: Log execution
        run: |
          echo "✅ Alertas enviadas el $(date)"
          echo "Timezone: UTC"
```

### 6.2 Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Secret 1:**
- Name: `ALERTS_ENDPOINT_URL`
- Value: `https://api.tudominio.com/api/emails/trigger-alerts/`

**Secret 2:**
- Name: `CRON_TOKEN`
- Value: (el mismo token que en `SECRET_CRON_TOKEN`)

### 6.3 Ejecutar Manualmente (para probar)

1. GitHub → **Actions**
2. Selecciona **Enviar Alertas Diarias**
3. **Run workflow** → **Run**

**📌 Nota sobre Timezones:**
- GitHub Actions usa **UTC**
- Colombia es **UTC-5** (sin horario de verano)
- Para ejecutar a las 8:00 AM Colombia: `0 13 * * *` (13:00 UTC)

---

## 📊 RESUMEN DE OPCIONES PARA ALERTAS

| Opción | Ventajas | Desventajas | Recomendada |
|--------|----------|-------------|-------------|
| **Cron en Servidor** | • Más rápido<br>• No depende de internet<br>• Gratis | • Requiere SSH | ✅ Sí |
| **Cron Externo** | • No requiere SSH<br>• Fácil de configurar | • Depende de servicio externo<br>• Requiere endpoint público | ⚠️ Si no tienes SSH |
| **GitHub Actions** | • Integrado con GitHub<br>• Logs visuales | • Limitado a 2000 min/mes (gratis)<br>• Depende de GitHub | ⚠️ Para proyectos pequeños |

---

## 🔍 TROUBLESHOOTING

### Problema: "CommandError: Conflicting migrations"

```bash
python manage.py makemigrations --merge
python manage.py migrate
```

### Problema: Cron no ejecuta el comando

**Verificar:**
```bash
# Ver si cron está corriendo
sudo service cron status
# o
sudo systemctl status cron

# Ver cron jobs
crontab -l

# Ver logs de cron
tail -f /var/log/syslog | grep CRON
```

**Solución:**
- Verifica rutas absolutas en el script
- Asegúrate de que el script sea ejecutable: `chmod +x`
- Verifica permisos del usuario que ejecuta cron

### Problema: Email no se envía

**Verificar:**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Mensaje de prueba', 'from@example.com', ['to@example.com'])
```

**Solución:**
- Verifica `GMAIL_PASSWORD` (debe ser App Password, no contraseña normal)
- Verifica `EMAIL_USE_TLS=True` y `EMAIL_PORT=587`
- Revisa logs: `tail -f /var/log/hr_alerts.log`

### Problema: Static files no se cargan (admin sin CSS)

```bash
python manage.py collectstatic
```

**Solución:**
- Verifica `STATIC_ROOT` en settings
- Asegúrate de que Coolify sirve `/static/`
- Considera usar WhiteNoise (ya en requirements.txt)

### Problema: "DisallowedHost at /"

**Solución:**
- Verifica `ALLOWED_HOSTS` en variables de entorno
- Debe incluir el dominio exacto: `api.tudominio.com`

### Problema: Gunicorn no inicia

**Verificar logs:**
- Coolify → Application → Logs

**Soluciones:**
- Verifica que gunicorn esté en `requirements.txt`
- Verifica el comando de start en Coolify
- Revisa errores de Python en el código

---

## ✅ CHECKLIST FINAL DE DEPLOYMENT

Antes de lanzar a producción:

### Configuración
- [ ] `requirements.txt` incluye gunicorn, psycopg2-binary, whitenoise
- [ ] `.gitignore` incluye `.env`, `media/`, `db.sqlite3`
- [ ] `.env.example` creado sin valores reales
- [ ] `media/` removido de Git

### Coolify
- [ ] PostgreSQL creado y conectado
- [ ] Variables de entorno configuradas (SECRET_KEY, DATABASE_URL, etc.)
- [ ] Dominio configurado con SSL
- [ ] Build command y Start command correctos

### Primer Deploy
- [ ] Deploy exitoso (sin errores en logs)
- [ ] API responde: `/api/`
- [ ] Admin carga: `/admin/`

### Inicialización (una sola vez)
- [ ] Superusuario creado
- [ ] Roles verificados (admin, cliente)
- [ ] Rol admin asignado al superusuario
- [ ] Obligation types existen
- [ ] Payment methods existen

### Alertas Automáticas
- [ ] Cron configurado (servidor, externo, o GitHub Actions)
- [ ] Alertas probadas manualmente
- [ ] Logs de alertas funcionan

### Seguridad
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` única y segura
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Gmail App Password (no contraseña normal)
- [ ] `SECRET_CRON_TOKEN` generado

---

## 📞 SOPORTE

**Documentación oficial:**
- Django: https://docs.djangoproject.com/
- Coolify: https://coolify.io/docs
- Gunicorn: https://docs.gunicorn.org/

**Fecha:** Febrero 2026  
**Versión:** 1.0
