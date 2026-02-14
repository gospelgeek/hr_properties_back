#!/bin/bash
# Script para ejecutar alertas automáticas
# Se ejecuta diariamente por cron a las 8:00 AM

cd /app
python manage.py send_due_alerts --alert-days 5 1 >> /var/log/alerts.log 2>&1
