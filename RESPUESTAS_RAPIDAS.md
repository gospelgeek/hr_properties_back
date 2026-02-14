# ❓ RESPUESTAS RÁPIDAS - Tus Preguntas

## 🤔 "¿El comando se ejecuta solo una vez o cada vez que quiero?"

**RESPUESTA:** El comando se ejecuta **AUTOMÁTICAMENTE TODOS LOS DÍAS** a la hora que programes.

**NO tienes que ejecutarlo manualmente** cada vez. Solo lo programas UNA VEZ y ya funciona solo.

---

## 📅 "¿Cómo funciona exactamente?"

**Lo que QUIERES:**
> Que cuando falten 5 días para vencer una obligación o renta, se envíe un correo automático al usuario.

**Cómo se LOGRA:**
1. Programas el comando para que se ejecute **todos los días a las 8:00 AM**
2. Cada día, el comando revisa automáticamente la base de datos
3. Si encuentra obligaciones/rentas que vencen en 5 días, envía los correos
4. Termina y espera hasta mañana 8 AM para ejecutarse de nuevo

**NO es a una hora específica que tú elijas cada día.**  
Es a la hora que lo programes **UNA VEZ** (por ejemplo 8 AM), y luego se repite solo todos los días a esa hora.

---

## ⚙️ "¿Cómo programo esto?"

### **Windows:**

1. **Abre el Programador de Tareas:**
   - Presiona `Windows + R`
   - Escribe `taskschd.msc`
   - Presiona Enter

2. **Crea la tarea:**
   - Clic en "Crear tarea básica..."
   - Nombre: "HR Properties - Alertas Diarias"
   - Trigger: **Diariamente** a las **8:00 AM**
   - Acción: Ejecutar el archivo `run_alerts.bat` de tu proyecto

3. **¡Listo!** Ya funciona solo todos los días

**Detalles paso a paso con imágenes en:** [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)

### **Linux (Producción):**

```bash
crontab -e

# Agregar esta línea:
0 8 * * * cd /ruta/proyecto && /ruta/venv/bin/python manage.py send_due_alerts
```

---

## 🔧 "¿Y los comandos como create_roles en producción?"

**RESPUESTA:** Esos comandos de inicialización se ejecutan **SOLO UNA VEZ**, la primera vez que despliegas.

### En tu computadora (desarrollo):
```bash
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
.\venv\Scripts\activate
python manage.py create_roles
python manage.py create_initial_data
```

### En el servidor (producción):

**Si tienes acceso SSH o RDP:**
```bash
# Conectarte al servidor
ssh usuario@servidor

# Ir a la carpeta del proyecto
cd /ruta/al/proyecto

# Activar entorno virtual
source venv/bin/activate

# Ejecutar comandos (solo la primera vez)
python manage.py migrate
python manage.py create_initial_data
python manage.py create_roles
python manage.py createsuperuser
```

### Script de inicialización (más fácil):

Ya creé un archivo `init_production.bat` que ejecuta TODOS los comandos de inicialización de una sola vez.

**En Windows:**
```bash
# Solo ejecutar la primera vez
init_production.bat
```

**En Linux:**
Ver: [GUIA_COMANDOS_PRODUCCION.md](GUIA_COMANDOS_PRODUCCION.md) para script completo.

---

## 📦 "¿Qué archivos ejecuto y cuándo?"

### **PRIMERA VEZ (Inicialización):**

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar TODO de una vez (Windows)
init_production.bat

# O manualmente:
python manage.py migrate
python manage.py create_initial_data
python manage.py create_roles
python manage.py createsuperuser
```

**Esto se ejecuta SOLO UNA VEZ**, cuando instalas el sistema por primera vez.

---

### **ALERTAS (Uso continuo):**

#### **Opción A: Manual (para probar)**
```bash
python manage.py send_due_alerts
```
Ejecuta esto **cuando quieras**, para probar que funciona.

#### **Opción B: Automático (producción)**
Programa en el **Programador de Tareas** para que ejecute `run_alerts.bat` todos los días.

**Se ejecuta AUTOMÁTICAMENTE** todos los días sin que hagas nada.

---

## 🔄 "¿Cuál es la diferencia?"

| Comando | Cuándo ejecutar | Cuántas veces |
|---------|----------------|---------------|
| `create_roles` | Primera vez | **UNA VEZ** |
| `create_initial_data` | Primera vez | **UNA VEZ** |
| `migrate` | Primera vez y actualizaciones | Cuando cambien modelos |
| `createsuperuser` | Primera vez | **UNA VEZ** (o para crear más admins) |
| `send_due_alerts` | Diariamente | **TODOS LOS DÍAS** (automático) |

---

## 📝 "¿Entonces qué hago ahora?"

### **Paso 1: Probar el comando de alertas**
```bash
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
.\venv\Scripts\activate
python manage.py send_due_alerts
```

Deberías ver en consola qué correos se enviarían.

### **Paso 2: Programar la tarea diaria**
Abre el Programador de Tareas y sigue la [GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)

### **Paso 3: Antes de producción**
Revisa el [CHECKLIST_PRODUCCION.md](CHECKLIST_PRODUCCION.md) para otros cambios importantes.

---

## 🎯 **RESUMEN ULTRA SIMPLE**

### Comandos de inicialización (`create_roles`, etc.):
- Se ejecutan **UNA VEZ** al principio
- En producción: los ejecutas cuando instalas el sistema por SSH/RDP
- Usar script `init_production.bat` es más fácil

### Comando de alertas (`send_due_alerts`):
- Se ejecuta **TODOS LOS DÍAS** automáticamente
- Lo programas UNA VEZ en el Programador de Tareas
- **NO tienes que ejecutarlo manualmente** cada día
- El sistema se encarga solo

---

## 📚 **Guías Completas**

- **[GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)** - Paso a paso con el Programador de Tareas
- **[EXPLICACION_VISUAL_ALERTAS.md](EXPLICACION_VISUAL_ALERTAS.md)** - Diagramas y ejemplos visuales
- **[GUIA_COMANDOS_PRODUCCION.md](GUIA_COMANDOS_PRODUCCION.md)** - Cómo ejecutar comandos en producción

---

¡Espero que ahora esté más claro! 🎉
