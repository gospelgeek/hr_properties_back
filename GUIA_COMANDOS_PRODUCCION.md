# 🚀 GUÍA: Comandos de Inicialización en Producción

Esta guía explica cómo ejecutar comandos de Django (como crear roles, poblar datos iniciales, etc.) en producción.

---

## 📋 COMANDOS COMUNES DE INICIALIZACIÓN

En tu proyecto tienes varios comandos de inicialización:

### 1. **Migraciones de Base de Datos**
```bash
python manage.py migrate
```
**Cuándo:** Primera vez que despliegas o después de cambios en modelos.

### 2. **Crear Superusuario**
```bash
python manage.py createsuperuser
```
**Cuándo:** Primera vez, para acceder al admin de Django.

### 3. **Crear Datos Iniciales (Finance)**
```bash
python manage.py create_initial_data
```
**Cuándo:** Primera vez, para poblar métodos de pago y tipos de obligaciones.

### 4. **Crear Roles de Usuario**
```bash
python manage.py create_roles
```
**Cuándo:** Primera vez, para crear los roles de usuario del sistema.

### 5. **Recolectar Archivos Estáticos**
```bash
python manage.py collectstatic --noinput
```
**Cuándo:** Antes de cada despliegue en producción.

---

## 🖥️ CÓMO EJECUTAR EN DIFERENTES ENTORNOS

### **LOCAL (Desarrollo)**

```bash
# Windows
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
.\venv\Scripts\activate
python manage.py comando_aqui

# Linux/Mac
cd /ruta/al/proyecto
source venv/bin/activate
python manage.py comando_aqui
```

---

### **PRODUCCIÓN - Windows Server**

#### Opción 1: Manualmente (SSH o RDP)

1. Conéctate al servidor
2. Abre PowerShell o CMD
3. Ejecuta:
```powershell
cd C:\ruta\al\proyecto
.\venv\Scripts\activate
python manage.py comando_aqui
```

#### Opción 2: Script de Inicialización

Crea un archivo `init_production.bat`:

```batch
@echo off
cd C:\ruta\al\proyecto
call venv\Scripts\activate.bat

echo Ejecutando migraciones...
python manage.py migrate

echo Creando datos iniciales...
python manage.py create_initial_data

echo Creando roles...
python manage.py create_roles

echo Recolectando archivos estáticos...
python manage.py collectstatic --noinput

echo.
echo ¡Inicialización completada!
pause
```

Ejecuta este script **solo la primera vez** que despliegues.

---

### **PRODUCCIÓN - Linux VPS (DigitalOcean, AWS, etc.)**

#### 1. Conectarse por SSH

```bash
ssh usuario@ip-del-servidor
```

#### 2. Navegar al proyecto

```bash
cd /var/www/hr-properties
# o la ruta donde esté tu proyecto
```

#### 3. Activar entorno virtual

```bash
source venv/bin/activate
```

#### 4. Ejecutar comandos

```bash
# Migraciones
python manage.py migrate

# Datos iniciales
python manage.py create_initial_data

# Roles
python manage.py create_roles

# Estáticos
python manage.py collectstatic --noinput
```

---

### **PRODUCCIÓN - Docker**

Si usas Docker:

```bash
# Entrar al contenedor
docker exec -it nombre-contenedor bash

# Ejecutar comandos
python manage.py migrate
python manage.py create_initial_data
python manage.py create_roles
```

---

### **PRODUCCIÓN - Servicios Cloud (Heroku, Railway, etc.)**

#### Heroku:
```bash
# Desde tu máquina local
heroku run python manage.py migrate
heroku run python manage.py create_initial_data
heroku run python manage.py create_roles
```

#### Railway:
```bash
railway run python manage.py migrate
railway run python manage.py create_initial_data
railway run python manage.py create_roles
```

---

## 📝 SCRIPT DE INICIALIZACIÓN COMPLETO

### Para Windows (`init_production.bat`)

```batch
@echo off
echo ========================================
echo HR PROPERTIES - Inicialización
echo ========================================
echo.

cd /d C:\ruta\al\proyecto
call venv\Scripts\activate.bat

REM Verificar variables de entorno
if not defined SECRET_KEY (
    echo ERROR: Variables de entorno no configuradas
    echo Por favor configura el archivo .env
    pause
    exit /b 1
)

echo [1/5] Ejecutando migraciones...
python manage.py migrate
if errorlevel 1 goto error

echo.
echo [2/5] Creando datos iniciales...
python manage.py create_initial_data
if errorlevel 1 goto error

echo.
echo [3/5] Creando roles de usuario...
python manage.py create_roles
if errorlevel 1 goto error

echo.
echo [4/5] Recolectando archivos estáticos...
python manage.py collectstatic --noinput
if errorlevel 1 goto error

echo.
echo [5/5] Verificando sistema...
python manage.py check --deploy
if errorlevel 1 goto error

echo.
echo ========================================
echo ✅ ¡Inicialización completada!
echo ========================================
echo.
echo Siguiente paso: Crear un superusuario
echo Ejecuta: python manage.py createsuperuser
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo ❌ Error en la inicialización
echo ========================================
pause
exit /b 1
```

### Para Linux (`init_production.sh`)

```bash
#!/bin/bash

echo "========================================"
echo "HR PROPERTIES - Inicialización"
echo "========================================"
echo ""

# Cambiar al directorio del proyecto
cd /var/www/hr-properties

# Activar entorno virtual
source venv/bin/activate

# Verificar variables de entorno
if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: Variables de entorno no configuradas"
    echo "Por favor configura el archivo .env"
    exit 1
fi

echo "[1/5] Ejecutando migraciones..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ Error en migraciones"
    exit 1
fi

echo ""
echo "[2/5] Creando datos iniciales..."
python manage.py create_initial_data
if [ $? -ne 0 ]; then
    echo "❌ Error creando datos iniciales"
    exit 1
fi

echo ""
echo "[3/5] Creando roles de usuario..."
python manage.py create_roles
if [ $? -ne 0 ]; then
    echo "❌ Error creando roles"
    exit 1
fi

echo ""
echo "[4/5] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "❌ Error recolectando estáticos"
    exit 1
fi

echo ""
echo "[5/5] Verificando sistema..."
python manage.py check --deploy
if [ $? -ne 0 ]; then
    echo "❌ Advertencias en verificación del sistema"
fi

echo ""
echo "========================================"
echo "✅ ¡Inicialización completada!"
echo "========================================"
echo ""
echo "Siguiente paso: Crear un superusuario"
echo "Ejecuta: python manage.py createsuperuser"
echo ""
```

**Hacer el script ejecutable:**
```bash
chmod +x init_production.sh
```

---

## 🔄 ORDEN DE EJECUCIÓN RECOMENDADO

### Primera vez (Deploy inicial):

```bash
1. python manage.py migrate
2. python manage.py create_initial_data
3. python manage.py create_roles
4. python manage.py createsuperuser
5. python manage.py collectstatic --noinput
```

### Actualizaciones posteriores:

```bash
1. python manage.py migrate
2. python manage.py collectstatic --noinput
3. # Reiniciar servidor web
```

---

## 🛡️ COMANDOS SEGUROS vs PELIGROSOS

### ✅ SEGUROS (puedes ejecutar varias veces)
- `migrate` - Aplica migraciones faltantes solamente
- `collectstatic` - Sobrescribe archivos estáticos
- `check` - Solo verifica, no modifica
- `send_due_alerts` - Envía emails, no modifica datos

### ⚠️ IDEMPOTENTES (seguros si están bien hechos)
- `create_initial_data` - Debería verificar si ya existen los datos
- `create_roles` - Debería verificar si ya existen los roles

### ❌ PELIGROSOS (solo en emergencias)
- `flush` - BORRA todos los datos
- `migrate --fake` - Marca migraciones como aplicadas sin ejecutarlas
- `createsuperuser` sin `--noinput` - Puede fallar en scripts

---

## 📋 CHECKLIST DE PRODUCCIÓN

Antes del primer deploy:

- [ ] Archivo `.env` configurado con valores de producción
- [ ] Base de datos creada (PostgreSQL)
- [ ] `python manage.py migrate` ejecutado
- [ ] `python manage.py create_initial_data` ejecutado
- [ ] `python manage.py create_roles` ejecutado
- [ ] `python manage.py createsuperuser` ejecutado
- [ ] `python manage.py collectstatic` ejecutado
- [ ] `python manage.py check --deploy` sin errores
- [ ] Servidor web configurado (Gunicorn, uWSGI, etc.)
- [ ] HTTPS configurado
- [ ] Backups configurados
- [ ] Logs configurados
- [ ] Alertas automáticas programadas

---

## ⚡ AUTOMATIZACIÓN CON CI/CD

Si usas GitHub Actions, GitLab CI, etc., puedes automatizar:

### Ejemplo GitHub Actions (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/hr-properties
            git pull
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
```

---

## 🆘 TROUBLESHOOTING

### Error: "No module named 'X'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error: "Settings.SECRET_KEY not set"
```bash
# Verificar .env
cat .env
# o en Windows:
type .env
```

### Error: "Permission denied"
```bash
# Linux - dar permisos al usuario
sudo chown -R usuario:usuario /var/www/hr-properties
```

### Error en migraciones
```bash
# Ver qué migraciones faltan
python manage.py showmigrations

# Ver SQL que se ejecutará (sin ejecutar)
python manage.py sqlmigrate app_name numero_migracion
```

---

## 📞 RESUMEN

1. **Primera vez:** Ejecuta todos los comandos de inicialización en orden
2. **Actualizaciones:** Solo `migrate` y `collectstatic`
3. **Scripts:** Usa los scripts de inicialización para automatizar
4. **CI/CD:** Automatiza el despliegue completo

---

**Última actualización:** Febrero 2026
