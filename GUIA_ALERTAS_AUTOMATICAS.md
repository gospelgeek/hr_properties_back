# 📧 GUÍA SIMPLE: Alertas Automáticas de Pagos

## 🎯 ¿Qué hace el sistema?

Todos los días (por ejemplo a las 8:00 AM), el sistema **automáticamente**:

1. **Revisa** todas las obligaciones y rentas
2. **Identifica** cuáles vencen en los próximos 5 días
3. **Envía correos** a los usuarios correspondientes recordándoles pagar

**TÚ NO TIENES QUE HACER NADA MANUALMENTE**. Solo configurarlo una vez.

---

## 🚀 CONFIGURACIÓN RÁPIDA (Windows)

### Paso 1: Probar el comando manualmente

Primero, prueba que funciona:

```bash
# Activar el entorno virtual
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
.\venv\Scripts\activate

# Ejecutar el comando
python manage.py send_due_alerts
```

Deberías ver en la consola qué correos se enviaron (o se intentaron enviar).

---

### Paso 2: Crear script de ejecución automática

Ya creé un archivo `run_alerts.bat` en tu proyecto. Este script:
- Activa el entorno virtual
- Ejecuta el comando de alertas
- Guarda un log de lo que pasó

---

### Paso 3: Programar ejecución diaria (Windows)

#### **Opción A: Programador de Tareas (GUI) - MÁS FÁCIL**

1. **Presiona** `Windows + R` y escribe `taskschd.msc`, presiona Enter
2. En el panel derecho, haz clic en **"Crear tarea básica..."**
3. **Nombre:** "HR Properties - Alertas Diarias"
4. **Descripción:** "Envía emails de recordatorio de pagos"
5. Haz clic en **"Siguiente"**

6. **Desencadenador (Trigger):**
   - Selecciona **"Diariamente"**
   - Haz clic en **"Siguiente"**
   - Hora: **08:00:00** (o la hora que prefieras)
   - Repetir cada: **1 días**
   - Haz clic en **"Siguiente"**

7. **Acción:**
   - Selecciona **"Iniciar un programa"**
   - Haz clic en **"Siguiente"**
   - **Programa o script:** Haz clic en "Examinar" y selecciona:
     ```
     C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties\run_alerts.bat
     ```
   - Haz clic en **"Siguiente"**

8. **Finalizar:**
   - Revisa que todo esté correcto
   - Marca la casilla **"Abrir el cuadro de diálogo Propiedades..."**
   - Haz clic en **"Finalizar"**

9. **En la ventana de Propiedades:**
   - Pestaña **"General"**: Marca **"Ejecutar con los privilegios más altos"**
   - Pestaña **"Configuración"**: Desmarca **"Detener la tarea si se ejecuta más de..."**
   - Haz clic en **"Aceptar"**

¡LISTO! Ahora todos los días a las 8 AM se enviarán las alertas automáticamente.

---

#### **Opción B: PowerShell (Más Rápido) - PARA TÉCNICOS**

Abre PowerShell **como Administrador** y ejecuta:

```powershell
$action = New-ScheduledTaskAction -Execute "C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties\run_alerts.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "HR Properties - Alertas Diarias" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Envía emails de recordatorio de pagos próximos a vencer"
```

---

### Paso 4: Verificar que funciona

Para probar que la tarea programada funciona:

1. Abre el **Programador de Tareas** (`taskschd.msc`)
2. Busca **"HR Properties - Alertas Diarias"** en la lista
3. Haz clic derecho → **"Ejecutar"**
4. Revisa el archivo de log: `logs/alerts.log`

---

## 📋 VERIFICAR LOGS

El sistema guarda un registro de todas las ejecuciones en:
```
C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties\logs\alerts.log
```

Puedes abrirlo con Notepad para ver:
- Qué día y hora se ejecutó
- Cuántos correos se enviaron
- Si hubo algún error

---

## 🔧 CAMBIAR CONFIGURACIÓN

### Cambiar los días de alertas

Por defecto envía alertas **5 días antes** y **1 día antes**. Para cambiar esto:

**Edita `run_alerts.bat`:**
```batch
REM Cambiar los días (puedes poner los que quieras)
REM Por defecto: 5 y 1 día antes
python manage.py send_due_alerts --alert-days 5 1

REM Ejemplo: Solo alertar 1 día antes
python manage.py send_due_alerts --alert-days 1

REM Ejemplo: Alertar 7, 3 y 1 días antes
python manage.py send_due_alerts --alert-days 7 3 1

REM Ejemplo: Solo el mismo día de vencimiento
python manage.py send_due_alerts --alert-days 0
```

**IMPORTANTE**: El sistema previene duplicados automáticamente. Si ejecutas el comando dos veces el mismo día, NO enviará correos duplicados.

### Cambiar la hora de ejecución

1. Abre el **Programador de Tareas**
2. Busca **"HR Properties - Alertas Diarias"**
3. Haz clic derecho → **"Propiedades"**
4. Pestaña **"Desencadenadores"**
5. Doble clic en el desencadenador
6. Cambia la hora
7. Guarda

---

## ❓ PREGUNTAS FRECUENTES

### ¿Cuántas veces se ejecuta?
**Una vez al día**, a la hora que configuraste.

### ¿Tengo que ejecutar el comando manualmente?
**NO**. Una vez configurado, se ejecuta automáticamente todos los días.

### ¿Qué pasa si la computadora está apagada?
Si usas el Programador de Tareas de Windows, puedes configurar que ejecute la tarea cuando enciendas la computadora (en Propiedades → Configuración → Marcar "Si la tarea no se pudo ejecutar...").

### ¿Cómo detengo las alertas?
1. Abre el **Programador de Tareas**
2. Busca **"HR Properties - Alertas Diarias"**
3. Haz clic derecho → **"Deshabilitar"** (o "Eliminar" si quieres borrarla)

### ¿Puedo ejecutar el comando manualmente cuando quiera?
**SÍ**. Puedes ejecutar:
```bash
python manage.py send_due_alerts
```
en cualquier momento para enviar alertas inmediatamente.

### ¿Los correos se envían de verdad?
En **desarrollo**, los correos se imprimen en la consola (no se envían).
En **producción**, debes configurar Gmail o SendGrid para que se envíen de verdad.
Ver: `PRODUCCION_EMAIL_CONFIG.md`

---

## 🚀 EN PRODUCCIÓN (Servidor)

### Linux (VPS, servidor en la nube)

Usa **cron** (viene preinstalado):

1. Edita el crontab:
```bash
crontab -e
```

2. Agrega esta línea:
```bash
# Ejecutar alertas todos los días a las 8:00 AM
0 8 * * * cd /ruta/al/proyecto && /ruta/al/venv/bin/python manage.py send_due_alerts >> /var/log/hr_alerts.log 2>&1
```

3. Guarda y cierra.

---

## 📝 RESUMEN

1. ✅ **Configurar una vez** el Programador de Tareas
2. ✅ El sistema **se ejecuta automáticamente** todos los días
3. ✅ **No tienes que hacer nada más**
4. ✅ Revisa los logs si quieres ver qué pasó

**¡Eso es todo!** 🎉
