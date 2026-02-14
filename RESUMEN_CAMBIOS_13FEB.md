# 📋 Resumen de Cambios - 13 de Febrero 2026

## ✅ 1. Organización de Archivos por Propiedad

### Problema Resuelto
Los archivos subidos (imágenes, documentos, vouchers) se guardaban todos en la misma carpeta sin organización.

### Solución Implementada
Ahora todos los archivos se organizan automáticamente en carpetas por propiedad:

```
media/
├── property_1/
│   ├── images/         # Imagen principal de la propiedad
│   ├── media/          # Galería de fotos/videos
│   ├── laws/           # Documentos legales
│   ├── ensers/         # Fotos de inventario
│   ├── payments/       # Vouchers de pagos de obligaciones
│   └── rentals/
│       ├── payments/   # Vouchers de pagos de rentas
│       └── contracts/  # Contratos y documentos de rentas
├── property_2/
│   └── ...
└── property_3/
    └── ...
```

### Archivos Modificados
- ✅ [models.py](apps/properties/models.py) - Agregadas funciones `upload_to`
- ✅ [models.py](apps/finance/models.py) - Función para vouchers de obligaciones
- ✅ [models.py](apps/rentals/models.py) - Funciones para archivos de rentas

### ⚠️ Acción Requerida
```bash
# Crear las migraciones
python manage.py makemigrations

# Aplicar las migraciones
python manage.py migrate
```

**NOTA**: Los archivos ya existentes NO se moverán automáticamente. Solo los nuevos archivos se organizarán correctamente.

---

## ✅ 2. Sistema de Correos Electrónicos

### ¿Cómo Funciona Actualmente?

El sistema **NO envía correos automáticamente por sí solo**. Necesitas configurarlo:

#### Configuración en Desarrollo (Consola)
Actualmente en `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Esto significa que los "correos" se imprimen en la **consola de Django**, no se envían realmente.

#### Configuración para Producción

Debes cambiar en `settings.py`:

**Opción 1: Gmail** (Más fácil para empezar)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-app-password'  # No tu contraseña normal
DEFAULT_FROM_EMAIL = 'tu-email@gmail.com'
```

**Opción 2: SendGrid** (Recomendado para producción)
```bash
pip install sendgrid
```

```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'tu-api-key'
DEFAULT_FROM_EMAIL = 'noreply@tudominio.com'
```

### ¿Cuándo se Envían los Correos?

Los correos se envían cuando ejecutas el comando:

```bash
python manage.py send_due_alerts
```

Este comando:
1. **Busca** obligaciones y rentas que vencen en días específicos (por defecto: 5 y 1 día antes)
2. **Verifica** que no se haya enviado ya esa alerta (previene duplicados)
3. **Envía** correos a los propietarios/inquilinos correspondientes

### ¿Cómo Automatizar el Envío?

**Opción A: Windows Task Scheduler** (Tu caso)

1. Ya tienes creados los scripts `run_alerts.bat` y `run_alerts.ps1`
2. Programa una tarea diaria en Windows (ver [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md))
3. El sistema ejecutará automáticamente el comando cada día

**Opción B: Cron (Linux/Mac)**
```bash
# Ejecutar todos los días a las 8:00 AM
0 8 * * * /ruta/al/proyecto/venv/bin/python /ruta/al/proyecto/manage.py send_due_alerts --alert-days 5 1
```

### Cambiar Días de Alerta

Por defecto: **5 días antes** y **1 día antes**.

Para cambiar, edita `run_alerts.bat`:
```batch
REM Solo 1 día antes
python manage.py send_due_alerts --alert-days 1

REM 7, 3 y 1 días antes
python manage.py send_due_alerts --alert-days 7 3 1

REM Solo el mismo día
python manage.py send_due_alerts --alert-days 0
```

### Documentación Disponible

- 📖 [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md) - Guía paso a paso
- 📖 [PRODUCCION_EMAIL_CONFIG.md](PRODUCCION_EMAIL_CONFIG.md) - Configuración de producción
- 📖 [EXPLICACION_VISUAL_ALERTAS.md](EXPLICACION_VISUAL_ALERTAS.md) - Explicación visual

---

## ✅ 3. Dashboard - Verificación de Datos

### Estadísticas del Dashboard

El dashboard (`GET /api/finance/dashboard/`) proporciona:

#### 📊 Obligaciones Globales
- **total_count**: Total de obligaciones (todas las propiedades)
- **total_amount**: Suma de todos los montos de obligaciones
- **total_paid**: Total pagado en todas las obligaciones
- **pending**: Monto pendiente por pagar
- **upcoming_due**: Obligaciones que vencen en los próximos 7 días

#### 📊 Obligaciones del Mes Actual
- **total_count**: Obligaciones que vencen este mes
- **total_amount**: Suma de montos de este mes
- **total_paid**: Total pagado este mes
- **pending**: Pendiente de este mes
- **upcoming_due**: Del mes que vencen en próximos 7 días

#### 🏠 Propiedades
- **total**: Total de propiedades activas (excluye soft-deleted)
- **by_use**: Desglose por uso (rental, personal, commercial)

#### 🏘️ Rentas
- **occupied**: Rentas activas
- **available**: Propiedades de renta disponibles
- **ending_soon**: Rentas que terminan en 15 días
- **monthly_occupied/available/ending_soon**: Desglose para rentas mensuales
- **airbnb_occupied/available/ending_soon**: Desglose para Airbnb

#### 💰 Resumen Financiero del Mes
- **rental_income**: Ingresos por pagos de rentas este mes
- **obligation_payments**: Gastos por pagos de obligaciones este mes
- **repair_costs**: Gastos por reparaciones este mes
- **net**: Neto del mes (ingresos - gastos)

### ✅ Los Datos Tienen Sentido
Todos los cálculos son correctos:
- Excluye propiedades soft-deleted
- Filtra correctamente por fechas
- Suma pagos de forma precisa

---

## ✅ 4. Obligaciones Recurrentes - Análisis

### El Problema

Actualmente, si tienes una obligación mensual (ej: cuota del banco):
- ❌ Debes crear **manualmente** cada mes una nueva obligación
- ❌ Si olvidas crearla, no aparecerá en el dashboard ni enviará alertas

### Soluciones Propuestas

He creado una guía completa: **[GUIA_OBLIGACIONES_RECURRENTES.md](GUIA_OBLIGACIONES_RECURRENTES.md)**

**Resumen de opciones**:

1. **Command Automático** ⭐ RECOMENDADO
   - Creas un comando que genera automáticamente las obligaciones del próximo mes
   - Fácil de implementar (30 minutos)
   - Se puede automatizar con Task Scheduler
   
2. **Modelo RecurringObligation**
   - Más robusto pero más complejo
   - Requiere migración de base de datos
   - Para cuando el sistema crezca

3. **Botón "Duplicar" en Frontend**
   - Más simple pero manual
   - No requiere código backend nuevo

### Recomendación Inmediata

1. Lee [GUIA_OBLIGACIONES_RECURRENTES.md](GUIA_OBLIGACIONES_RECURRENTES.md)
2. Decide qué opción implementar
3. Si eliges la Opción 1 (recomendada), puedo implementarla en 30 minutos

---

## 📝 Próximos Pasos

### Urgente
1. ✅ **Crear migraciones**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. ✅ **Decidir sobre configuración de emails**:
   - ¿Usar Gmail o SendGrid?
   - Configurar credenciales en `settings.py`

3. ✅ **Probar el sistema de alertas**:
   ```bash
   python manage.py send_due_alerts
   ```

### Recomendado
4. ⭐ **Implementar sistema de obligaciones recurrentes** (Opción 1)
5. ⭐ **Programar Task Scheduler** para alertas automáticas diarias
6. ⭐ **Probar en producción** con datos reales

---

## 🎉 Resumen Final

### Lo que se Corrigió
✅ Organización de archivos por propiedad (ya no están todos mezclados)
✅ Sistema de alertas con días específicos (no spam diario)
✅ Dashboard con estadísticas correctas
✅ Documentación completa sobre correos y obligaciones recurrentes

### Lo que Debes Hacer
1. Ejecutar migraciones
2. Configurar email backend (Gmail o SendGrid)
3. Decidir si implementar sistema de obligaciones recurrentes
4. Probar el sistema de alertas

### Archivos Importantes
- [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)
- [GUIA_OBLIGACIONES_RECURRENTES.md](GUIA_OBLIGACIONES_RECURRENTES.md)
- [PRODUCCION_EMAIL_CONFIG.md](PRODUCCION_EMAIL_CONFIG.md)

¿Necesitas ayuda con alguno de estos pasos? ¡Solo pregunta!
