# ========================================
# Script PowerShell para ejecutar alertas automáticas
# HR Properties - Sistema de notificaciones
# ========================================

# Variables de configuración
$ProjectPath = "C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties"
$VenvPath = "$ProjectPath\venv\Scripts\python.exe"
$LogsPath = "$ProjectPath\logs"
$AlertDays = @(5, 1)  # Días de anticipación para alertas (5 días antes y 1 día antes)

# Cambiar al directorio del proyecto
Set-Location $ProjectPath

# Crear carpeta de logs si no existe
if (!(Test-Path $LogsPath)) {
    New-Item -ItemType Directory -Path $LogsPath | Out-Null
}

# Registrar inicio
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Output "`n========================================" | Tee-Object -FilePath "$LogsPath\alerts.log" -Append
Write-Output "Ejecutando alertas - $timestamp" | Tee-Object -FilePath "$LogsPath\alerts.log" -Append
Write-Output "========================================" | Tee-Object -FilePath "$LogsPath\alerts.log" -Append

# Ejecutar el comando de alertas
& $VenvPath manage.py send_due_alerts --alert-days $AlertDays 2>&1 | Tee-Object -FilePath "$LogsPath\alerts.log" -Append

# Registrar finalización
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Output "`n========================================" | Tee-Object -FilePath "$LogsPath\alerts.log" -Append
Write-Output "Alertas ejecutadas - $timestamp" | Tee-Object -FilePath "$LogsPath\alerts.log" -Append
Write-Output "========================================`n" | Tee-Object -FilePath "$LogsPath\alerts.log" -Append

Write-Host "`n✅ Alertas ejecutadas correctamente. Revisa logs\alerts.log para más detalles." -ForegroundColor Green
