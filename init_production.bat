@echo off
REM ========================================
REM HR PROPERTIES - Script de Inicialización
REM Ejecutar SOLO la primera vez en producción
REM ========================================

echo.
echo ========================================
echo   HR PROPERTIES - Inicialización
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties

REM Activar entorno virtual
call venv\Scripts\activate.bat

echo [1/6] Verificando instalación de dependencias...
pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [2/6] Ejecutando migraciones de base de datos...
python manage.py migrate
if errorlevel 1 goto error

echo.
echo [3/6] Creando datos iniciales (métodos de pago, tipos de obligaciones)...
python manage.py create_initial_data
if errorlevel 1 goto error

echo.
echo [4/6] Creando roles de usuario del sistema...
python manage.py create_roles
if errorlevel 1 goto error

echo.
echo [5/6] Recolectando archivos estáticos...
python manage.py collectstatic --noinput
if errorlevel 1 goto error

echo.
echo [6/6] Verificando configuración del sistema...
python manage.py check --deploy

echo.
echo ========================================
echo   ¡Inicialización completada!
echo ========================================
echo.
echo SIGUIENTE PASO:
echo   Ejecuta: python manage.py createsuperuser
echo   Para crear el usuario administrador
echo.
echo PARA ACTIVAR ALERTAS AUTOMÁTICAS:
echo   1. Ejecuta: run_alerts.bat (para probar)
echo   2. Programa la tarea en el Programador de Tareas
echo      (Ver GUIA_ALERTAS_AUTOMATICAS.md)
echo.
pause
goto end

:error
echo.
echo ========================================
echo   ❌ Error en la inicialización
echo ========================================
echo.
echo Revisa los mensajes de error arriba
pause
exit /b 1

:end
call venv\Scripts\deactivate.bat
