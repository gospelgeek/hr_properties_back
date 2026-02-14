FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . /app/

# Crear directorio de logs
RUN mkdir -p /var/log

# Copiar y configurar script de cron para alertas
COPY cron_alerts.sh /app/cron_alerts.sh
RUN chmod +x /app/cron_alerts.sh
RUN echo "0 8 * * * /app/cron_alerts.sh" | crontab -

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Exponer puerto
EXPOSE 8000

# Comando de inicio: cron + gunicorn
CMD cron && gunicorn hr_properties.wsgi:application --bind 0.0.0.0:8000 --workers 3
