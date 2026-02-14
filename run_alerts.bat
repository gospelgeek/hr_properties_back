@echo off
REM ========================================
REM Script para ejecutar alertas automáticas
REM HR Properties - Sistema de notificaciones
REM ========================================

REM Cambiar al directorio del proyecto
cd /d C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties

REM Activar el entorno virtual
call venv\Scripts\activate.bat

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

REM Ejecutar el comando de alertas
REM --alert-days 5 1 significa que alertará 5 días antes Y 1 día antes del vencimiento
REM Puedes cambiar los números según necesites (ej: --alert-days 7 3 1)
echo ========================================
echo Ejecutando alertas - %date% %time%
echo ========================================
python manage.py send_due_alerts --alert-days 5 1 >> logs\alerts.log 2>&1

REM Registrar finalización
echo.
echo ========================================
echo Alertas ejecutadas - %date% %time%
echo ========================================
echo.

REM Desactivar entorno virtual
call venv\Scripts\deactivate.bat

REM Pausar solo si se ejecuta manualmente (para ver el resultado)
REM Comentar esta línea si se ejecuta desde el Programador de Tareas
REM pause
