# 🎯 Entendiendo las Alertas Automáticas - Explicación Visual

## 📅 ¿Cómo funciona el sistema día a día?

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE ALERTAS                         │
└─────────────────────────────────────────────────────────────┘

       CADA DÍA A LAS 8:00 AM (Programado)
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   🤖 Sistema se ejecuta solo      │
    │   python manage.py send_due_alerts│
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   📋 Revisa TODA la base de datos:│
    │   • Obligaciones                  │
    │   • Rentas                        │
    │   • Pagos pendientes              │
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   🔍 Identifica cuáles vencen     │
    │   en los próximos 5 días          │
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   📧 Envía correos a:             │
    │   • Propietarios (obligaciones)   │
    │   • Inquilinos (rentas/pagos)     │
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   ✅ Guarda log de lo que hizo    │
    │   logs/alerts.log                 │
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   😴 Termina hasta mañana 8 AM    │
    └───────────────────────────────────┘
```

---

## 📊 Ejemplo Práctico

### Escenario:

```
HOY: 10 de Febrero de 2026

BASE DE DATOS:
┌─────────────────────────────────────────────────────────┐
│ Obligación 1: Vence el 15 de Feb (en 5 días) ❗        │
│ Obligación 2: Vence el 28 de Feb (en 18 días)          │
│ Renta 1: Vence el 12 de Feb (en 2 días) ❗             │
│ Renta 2: Vence el 14 de Feb (en 4 días) ❗             │
│ Renta 3: Vence el 25 de Feb (en 15 días)               │
└─────────────────────────────────────────────────────────┘
```

### A las 8:00 AM del 10 de Febrero:

```
🤖 Sistema ejecuta: send_due_alerts

🔍 Busca lo que vence entre HOY y dentro de 5 días
    (del 10 al 15 de Febrero)

✅ Encuentra:
    • Obligación 1 (vence el 15) ➜ Envía email al propietario
    • Renta 1 (vence el 12)      ➜ Envía email al inquilino
    • Renta 2 (vence el 14)      ➜ Envía email al inquilino

❌ NO envía para:
    • Obligación 2 (faltan 18 días, fuera del rango)
    • Renta 3 (faltan 15 días, fuera del rango)

📝 Guarda en logs/alerts.log:
    "2026-02-10 08:00 - Enviados 3 emails"
```

### Al día siguiente (11 de Febrero a las 8:00 AM):

```
🤖 Sistema se ejecuta DE NUEVO automáticamente

🔍 Busca lo que vence entre HOY y dentro de 5 días
    (del 11 al 16 de Febrero)

✅ Encuentra:
    • Obligación 1 (vence el 15) ➜ Envía email OTRA VEZ
    • Renta 1 (vence el 12)      ➜ Envía email OTRA VEZ
    • Renta 2 (vence el 14)      ➜ Envía email OTRA VEZ

📧 Los usuarios reciben OTRO recordatorio
   (cada día hasta que paguen o venza)
```

---

## 🤔 Preguntas y Respuestas

### ❓ ¿El comando se ejecuta solo una vez?

**NO**. Se ejecuta TODOS LOS DÍAS automáticamente.

```
Lunes 8 AM   ➜ ✅ Se ejecuta
Martes 8 AM  ➜ ✅ Se ejecuta
Miércoles... ➜ ✅ Se ejecuta
Jueves...    ➜ ✅ Se ejecuta
...SIEMPRE   ➜ ✅ Se ejecuta
```

---

### ❓ ¿Y si no quiero que se ejecute un día?

**Opción 1:** Deshabilita la tarea programada ese día

**Opción 2:** Borra temporalmente la tarea del Programador

**Opción 3:** El sistema simplemente no enviará emails si no hay nada próximo a vencer

---

### ❓ ¿Los usuarios reciben múltiples correos?

**SÍ**, si no pagan. Ejemplo:

```
Día 1 (faltan 5 días): 📧 "Tu obligación vence en 5 días"
Día 2 (faltan 4 días): 📧 "Tu obligación vence en 4 días"
Día 3 (faltan 3 días): 📧 "Tu obligación vence en 3 días"
...

Esto es INTENCIONAL para recordarles que paguen.
```

Si NO quieres que reciban múltiples correos, deberías modificar el código para:
- Solo enviar UNA VEZ (registrar que ya se envió)
- O enviar solo ciertos días (ej: 5 días antes y 1 día antes)

---

### ❓ ¿Puedo cambiar cuántos días de anticipación?

**SÍ**. Edita el archivo `run_alerts.bat`:

```batch
REM Cambiar --days 5 por otro número

REM Para 3 días:
python manage.py send_due_alerts --days 3

REM Para 7 días:
python manage.py send_due_alerts --days 7

REM Para 10 días:
python manage.py send_due_alerts --days 10
```

---

### ❓ ¿Puedo ejecutar el comando manualmente cuando quiera?

**SÍ**. Abre una terminal y ejecuta:

```bash
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
.\venv\Scripts\activate
python manage.py send_due_alerts
```

Esto enviará alertas INMEDIATAMENTE (sin esperar a las 8 AM).

---

### ❓ ¿Cómo sé si funcionó?

**Opción 1:** Revisa el archivo de logs

```
logs/alerts.log
```

**Opción 2:** En desarrollo, los emails se imprimen en la consola

**Opción 3:** En producción, revisa la bandeja de entrada de los usuarios

---

## 🛠️ Configuración Paso a Paso

### 1️⃣ **PROBAR manualmente (primero)**

```bash
# Abre PowerShell o CMD
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
.\venv\Scripts\activate
python manage.py send_due_alerts

# Deberías ver algo como:
# ========================================
# INICIANDO ENVÍO DE ALERTAS - 2026-02-10
# Alertando con 5 días de anticipación
# ========================================
# 
# [1] Verificando obligaciones próximas a vencer...
#   ✓ Alerta enviada: Impuesto Predial -> owner@example.com
# 
# Obligaciones: 1 alertas enviadas de 1 encontradas
# ...
```

---

### 2️⃣ **PROGRAMAR para que se ejecute solo**

Sigue la [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)

En resumen:
1. Abre el Programador de Tareas (Win + R, escribe `taskschd.msc`)
2. Crea tarea básica
3. Nombre: "HR Properties - Alertas Diarias"
4. Trigger: Diario a las 8:00 AM
5. Acción: Ejecutar `run_alerts.bat`
6. Guardar

---

### 3️⃣ **VERIFICAR que funciona**

1. En el Programador de Tareas, busca la tarea
2. Clic derecho ➜ "Ejecutar"
3. Revisa `logs/alerts.log`

---

## 📝 Resumen Ultra Simple

```
┌──────────────────────────────────────────────────────┐
│  ¿QUÉ HACE?                                          │
│  Envía correos recordando pagos próximos a vencer    │
│                                                       │
│  ¿CUÁNDO?                                            │
│  Todos los días a las 8:00 AM (automático)           │
│                                                       │
│  ¿CÓMO LO CONFIGURO?                                 │
│  1. Ejecuta manualmente para probar                  │
│  2. Programa en el Programador de Tareas             │
│  3. ¡Listo! Ya no tienes que hacer nada más          │
│                                                       │
│  ¿TENGO QUE HACER ALGO CADA DÍA?                     │
│  NO. Se ejecuta solo automáticamente.                │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 Próximos Pasos

1. ✅ Lee esta guía
2. ✅ Ejecuta manualmente: `python manage.py send_due_alerts`
3. ✅ Verifica que funciona (revisa logs o consola)
4. ✅ Programa la tarea (ver GUIA_ALERTAS_AUTOMATICAS.md)
5. ✅ Olvídate, ya funciona solo 😎

---

**¿Dudas?** Revisa las otras guías:
- [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md) - Programar la tarea
- [GUIA_COMANDOS_PRODUCCION.md](GUIA_COMANDOS_PRODUCCION.md) - Comandos en producción
- [PRODUCCION_EMAIL_CONFIG.md](PRODUCCION_EMAIL_CONFIG.md) - Configurar email real
