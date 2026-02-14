# 🚀 Sistema Simplificado - Correos y Obligaciones Automáticas

## 🎯 Tu Visión vs Realidad Actual

### Lo que NO te gusta (Sistema Actual):
❌ Comandos manuales (`send_due_alerts`)  
❌ Task Scheduler de Windows  
❌ Demasiado complejo  
❌ Muchos archivos y documentación  

### Lo que QUIERES:
✅ Automático - sin ejecutar nada manualmente  
✅ Simple - cuando se crea/actualiza algo, verificar y enviar  
✅ Obligaciones recurrentes automáticas cada mes  
✅ Usar Celery (mencionaste)  

---

## 💡 Solución Propuesta: Django Signals + Celery Beat

### Arquitectura Simplificada

```
1. Usuario crea/actualiza Obligación o Renta
        ↓
2. Django Signal detecta el cambio
        ↓
3. Signal verifica: ¿Faltan 5 o 1 día para vencimiento?
        ↓
4. Si SÍ → Programa tarea en Celery para enviar correo
        ↓
5. Celery envía el correo en segundo plano
```

**Ventajas**:
- 🎯 No necesitas ejecutar comandos
- 🎯 No necesitas Task Scheduler
- 🎯 Todo es automático
- 🎯 Celery maneja la cola de correos
- 🎯 Celery Beat crea obligaciones recurrentes cada mes

---

## 📋 Parte 1: Instalación de Celery

### Paso 1: Instalar dependencias

```bash
pip install celery redis python-dateutil
```

### Paso 2: Instalar Redis (Broker de Celery)

**Windows**:
1. Descargar desde: https://github.com/microsoftarchive/redis/releases
2. Instalar Redis-x64-3.0.504.msi
3. Redis se ejecutará como servicio automáticamente

**O usar Docker**:
```bash
docker run -d -p 6379:6379 redis
```

### Paso 3: Configurar Celery

**Crear `hr_properties/celery.py`**:

```python
import os
from celery import Celery
from celery.schedules import crontab

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_properties.settings')

app = Celery('hr_properties')

# Cargar configuración desde settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en cada app
app.autodiscover_tasks()

# Configurar tareas periódicas
app.conf.beat_schedule = {
    # Crear obligaciones recurrentes - cada día 25 del mes a las 8:00 AM
    'create-recurring-obligations': {
        'task': 'apps.finance.tasks.create_next_month_obligations',
        'schedule': crontab(day_of_month='25', hour=8, minute=0),
    },
    # Enviar alertas diarias - todos los días a las 8:00 AM
    'send-daily-alerts': {
        'task': 'apps.emails.tasks.send_daily_alerts',
        'schedule': crontab(hour=8, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

**Actualizar `hr_properties/__init__.py`**:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

**Actualizar `settings.py`**:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'  # Ajusta a tu zona horaria
```

---

## 📋 Parte 2: Sistema de Correos con Signals

### Crear `apps/emails/tasks.py` (Tareas Celery):

```python
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.finance.models import Obligation
from apps.rentals.models import Rental
from apps.emails.models import AlertSent
from apps.emails.utils import send_obligation_alert, send_rental_due_alert
from django.contrib.contenttypes.models import ContentType


@shared_task(name='apps.emails.tasks.send_obligation_email')
def send_obligation_email(obligation_id, days_before):
    """Enviar correo para una obligación específica"""
    try:
        obligation = Obligation.objects.get(id=obligation_id)
        
        # Determinar tipo de alerta
        alert_type = f'{days_before}_days' if days_before > 0 else 'same_day'
        
        # Verificar si ya se envió
        content_type = ContentType.objects.get_for_model(Obligation)
        already_sent = AlertSent.objects.filter(
            content_type=content_type,
            object_id=obligation.id,
            alert_type=alert_type
        ).exists()
        
        if already_sent:
            return f"Ya enviado: {obligation.entity_name}"
        
        # Enviar correo
        if hasattr(obligation.property, 'owner') and hasattr(obligation.property.owner, 'email'):
            send_obligation_alert(obligation, obligation.property.owner.email, days_before)
            
            # Registrar envío
            AlertSent.objects.create(
                content_type=content_type,
                object_id=obligation.id,
                alert_type=alert_type
            )
            
            return f"✓ Correo enviado: {obligation.entity_name}"
        
        return f"Sin email: {obligation.entity_name}"
    
    except Obligation.DoesNotExist:
        return f"Obligación {obligation_id} no existe"


@shared_task(name='apps.emails.tasks.send_rental_email')
def send_rental_email(rental_id, days_before):
    """Enviar correo para una renta específica"""
    try:
        rental = Rental.objects.get(id=rental_id)
        
        # Determinar tipo de alerta
        alert_type = f'{days_before}_days' if days_before > 0 else 'same_day'
        
        # Verificar si ya se envió
        content_type = ContentType.objects.get_for_model(Rental)
        already_sent = AlertSent.objects.filter(
            content_type=content_type,
            object_id=rental.id,
            alert_type=alert_type
        ).exists()
        
        if already_sent:
            return f"Ya enviado: {rental.property.name}"
        
        # Enviar correo
        if rental.tenant and rental.tenant.email:
            send_rental_due_alert(rental, rental.tenant.email, days_before)
            
            # Registrar envío
            AlertSent.objects.create(
                content_type=content_type,
                object_id=rental.id,
                alert_type=alert_type
            )
            
            return f"✓ Correo enviado: {rental.property.name}"
        
        return f"Sin email: {rental.property.name}"
    
    except Rental.DoesNotExist:
        return f"Renta {rental_id} no existe"


@shared_task(name='apps.emails.tasks.send_daily_alerts')
def send_daily_alerts():
    """Tarea periódica: Verificar y enviar alertas diarias"""
    today = timezone.now().date()
    sent_count = 0
    
    # Alertas para 5 y 1 día antes
    alert_days = [5, 1]
    
    for days in alert_days:
        target_date = today + timedelta(days=days)
        
        # Obligaciones que vencen en target_date
        obligations = Obligation.objects.filter(
            due_date=target_date,
            property__is_deleted__isnull=True
        )
        
        for obligation in obligations:
            send_obligation_email.delay(obligation.id, days)
            sent_count += 1
        
        # Rentas que vencen en target_date
        rentals = Rental.objects.filter(
            check_out=target_date,
            status='occupied'
        )
        
        for rental in rentals:
            send_rental_email.delay(rental.id, days)
            sent_count += 1
    
    return f"✓ {sent_count} correos programados"
```

### Crear `apps/emails/signals.py` (Opcional - Envío inmediato):

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from apps.finance.models import Obligation
from apps.rentals.models import Rental
from apps.emails.tasks import send_obligation_email, send_rental_email


@receiver(post_save, sender=Obligation)
def check_obligation_due_date(sender, instance, created, **kwargs):
    """
    Cuando se crea/actualiza una obligación, verificar si está a 5 o 1 día de vencer
    y programar envío de correo
    """
    if not instance.property.is_deleted:
        today = timezone.now().date()
        days_until_due = (instance.due_date - today).days
        
        # Si faltan 5 o 1 día, programar envío
        if days_until_due in [5, 1]:
            send_obligation_email.delay(instance.id, days_until_due)


@receiver(post_save, sender=Rental)
def check_rental_ending(sender, instance, created, **kwargs):
    """
    Cuando se crea/actualiza una renta, verificar si está a 5 o 1 día de terminar
    y programar envío de correo
    """
    if instance.status == 'occupied':
        today = timezone.now().date()
        days_until_end = (instance.check_out - today).days
        
        # Si faltan 5 o 1 día, programar envío
        if days_until_end in [5, 1]:
            send_rental_email.delay(instance.id, days_until_end)
```

### Registrar signals en `apps/emails/apps.py`:

```python
from django.apps import AppConfig


class EmailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.emails'
    
    def ready(self):
        import apps.emails.signals  # Registrar signals
```

---

## 📋 Parte 3: Obligaciones Recurrentes Automáticas

### Crear `apps/finance/tasks.py`:

```python
from celery import shared_task
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.finance.models import Obligation


@shared_task(name='apps.finance.tasks.create_next_month_obligations')
def create_next_month_obligations():
    """
    Tarea periódica: Crear automáticamente obligaciones del próximo mes
    Se ejecuta cada día 25 del mes a las 8:00 AM
    """
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    next_month_start = current_month_start + relativedelta(months=1)
    
    # Buscar obligaciones recurrentes de este mes
    obligations = Obligation.objects.filter(
        due_date__gte=current_month_start,
        due_date__lt=next_month_start,
        property__is_deleted__isnull=True
    ).exclude(temporality='one_time')
    
    created_count = 0
    
    for obligation in obligations:
        # Calcular nueva fecha de vencimiento
        if obligation.temporality == 'monthly':
            new_due_date = obligation.due_date + relativedelta(months=1)
        elif obligation.temporality == 'bimonthly':
            new_due_date = obligation.due_date + relativedelta(months=2)
        elif obligation.temporality == 'quarterly':
            new_due_date = obligation.due_date + relativedelta(months=3)
        elif obligation.temporality == 'biannual':
            new_due_date = obligation.due_date + relativedelta(months=6)
        elif obligation.temporality == 'annual':
            new_due_date = obligation.due_date + relativedelta(years=1)
        elif obligation.temporality == 'weekly':
            new_due_date = obligation.due_date + relativedelta(weeks=1)
        else:
            continue
        
        # Verificar que no exista ya
        exists = Obligation.objects.filter(
            property=obligation.property,
            entity_name=obligation.entity_name,
            due_date=new_due_date
        ).exists()
        
        if not exists:
            # Crear nueva obligación
            Obligation.objects.create(
                property=obligation.property,
                obligation_type=obligation.obligation_type,
                entity_name=obligation.entity_name,
                amount=obligation.amount,
                due_date=new_due_date,
                temporality=obligation.temporality
            )
            created_count += 1
    
    return f"✓ {created_count} obligaciones creadas para el próximo período"
```

---

## 🚀 Parte 4: Ejecutar Celery

### En Desarrollo (Windows):

**Terminal 1 - Worker** (procesa tareas):
```bash
celery -A hr_properties worker -l info --pool=solo
```

**Terminal 2 - Beat** (programa tareas periódicas):
```bash
celery -A hr_properties beat -l info
```

**Terminal 3 - Django** (servidor):
```bash
python manage.py runserver
```

### En Producción (Linux):

**Supervisord o systemd** para mantener Celery corriendo:

```ini
# /etc/supervisor/conf.d/celery.conf
[program:celery_worker]
command=/path/to/venv/bin/celery -A hr_properties worker -l info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true

[program:celery_beat]
command=/path/to/venv/bin/celery -A hr_properties beat -l info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
```

---

## 📊 Comparación: Antes vs Después

### ANTES (Sistema Actual):
```
❌ Ejecutar comando manualmente: python manage.py send_due_alerts
❌ Programar en Task Scheduler de Windows
❌ Crear obligaciones mes a mes manualmente
❌ Muchos archivos: run_alerts.bat, run_alerts.ps1, comandos, etc.
❌ Documentación extensa
```

### DESPUÉS (Sistema Nuevo):
```
✅ Celery Beat ejecuta tareas automáticamente
✅ Signals detectan cambios y programan correos
✅ Obligaciones recurrentes se crean solas cada mes
✅ Todo centralizado en tasks.py
✅ Más robusto y escalable
```

---

## 🎯 Decisión: ¿Implementar Celery o Mantener Sistema Actual?

### Celery (Recomendado):
**Pros**:
- ✅ Totalmente automático
- ✅ No necesitas Task Scheduler
- ✅ Escalable (puede procesar miles de correos)
- ✅ Manejo de errores robusto
- ✅ Estándar de la industria

**Contras**:
- ❌ Requiere Redis (servidor adicional)
- ❌ Más complejo de configurar inicialmente
- ❌ 3 procesos corriendo (Django + Worker + Beat)

### Sistema Actual (Task Scheduler):
**Pros**:
- ✅ Ya implementado
- ✅ Funciona sin dependencias adicionales
- ✅ Simple para proyectos pequeños

**Contras**:
- ❌ Solo funciona en Windows
- ❌ Requiere configuración manual
- ❌ No escala bien
- ❌ Obligaciones recurrentes siguen siendo manuales

---

## 💬 Mi Recomendación

**Para desarrollo**: Mantén el sistema actual (Task Scheduler) mientras aprendes Celery.

**Para producción**: Implementa Celery. Es la solución profesional y escalable.

### Ruta de implementación gradual:

1. **Fase 1** (Esta semana): 
   - ✅ Corregir Zelle y obligation types (YA HECHO)
   - Mantener sistema actual funcionando

2. **Fase 2** (Próxima semana):
   - Instalar Redis y Celery
   - Migrar sistema de alertas a Celery tasks
   - Probar en desarrollo

3. **Fase 3** (Después):
   - Implementar obligaciones recurrentes con Celery Beat
   - Migrar a producción con supervisord

---

## ❓ ¿Qué prefieres?

1. **Implementar Celery ahora** (te ayudo paso a paso)
2. **Mantener sistema actual** y mejorar en el futuro
3. **Híbrido**: Celery para obligaciones recurrentes, Task Scheduler para alertas

Dime qué prefieres y te ayudo con la implementación.
