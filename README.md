# 🏠 HR Properties - Sistema de Gestión de Propiedades

Sistema completo de gestión de propiedades con alquileres, finanzas, mantenimiento, autenticación dual y alertas automáticas.

## 📋 Características

- **🏘️ Gestión de Propiedades**: CRUD completo de propiedades con multimedia
- **📄 Alquileres**: Manejo de contratos mensuales, Airbnb y diarios
- **💰 Finanzas**: Obligaciones, pagos, métodos de pago y dashboard
- **🔧 Mantenimiento**: Registro de reparaciones y enseres
- **📧 Alertas Automáticas**: Sistema de notificaciones por email para:
  - Obligaciones próximas a vencer
  - Rentas próximas a vencer
  - Pagos pendientes
- **🔐 Autenticación Dual**:
  - Google OAuth para administradores
  - Credenciales (teléfono + año) para clientes
- **👥 Sistema de Roles**: Admin, Cliente, Invitado

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd hr-properties

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

Crear archivo `.env` en la raíz:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Admin Emails (separados por comas)
ADMIN_EMAILS=admin1@company.com,admin2@company.com
```

### 3. Migraciones

```bash
python manage.py migrate
```

### 4. Inicializar Datos del Sistema

```bash
# Crear datos iniciales (métodos de pago, tipos de obligaciones)
python manage.py create_initial_data

# Crear roles de usuario
python manage.py create_roles

# O ejecutar todo con un solo script (Windows):
init_production.bat
```

### 5. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 6. Inicializar Autenticación (Opcional)

```bash
python init_auth.py
```

Este script:
- ✅ Crea roles (admin, cliente, invitado)
- ✅ Verifica configuraciones
- ✅ Permite crear un tenant de prueba

### 7. Ejecutar Servidor

```bash
python manage.py runserver
```

### 8. Probar Alertas Automáticas (Opcional)

```bash
# Ejecutar comando de alertas manualmente
python manage.py send_due_alerts

# Programar ejecución automática diaria
# Ver: GUIA_ALERTAS_AUTOMATICAS.md
```

## 📚 Documentación

### Guías de Usuario
- **[GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)**: Guía completa para configurar alertas automáticas
- **[EXPLICACION_VISUAL_ALERTAS.md](EXPLICACION_VISUAL_ALERTAS.md)**: Explicación visual del funcionamiento de alertas

### Guías de Producción
- **[CHECKLIST_PRODUCCION.md](CHECKLIST_PRODUCCION.md)**: Lista de verificación antes de producción
- **[GUIA_COMANDOS_PRODUCCION.md](GUIA_COMANDOS_PRODUCCION.md)**: Cómo ejecutar comandos en producción
- **[PRODUCCION_EMAIL_CONFIG.md](PRODUCCION_EMAIL_CONFIG.md)**: Configuración de email para producción

### Documentación Técnica
- **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)**: Guía completa de configuración de autenticación
- **[AUTHENTICATION_IMPLEMENTATION_SUMMARY.md](AUTHENTICATION_IMPLEMENTATION_SUMMARY.md)**: Resumen de implementación
- **[apps/users/urls.py](apps/users/urls.py)**: Documentación de endpoints de autenticación
- **[apps/users/permissions.py](apps/users/permissions.py)**: Permisos y ejemplos de uso
- **[apps/emails/README.md](apps/emails/README.md)**: Documentación del sistema de emails

## 🔐 Autenticación

### Login de Clientes (Credenciales)

```bash
POST /api/users/login/
{
  "username": "3123456789",      // teléfono del tenant
  "password": "31234567891990"   // teléfono + año de nacimiento
}
```

### Login de Admins (Google OAuth)

```bash
POST /api/users/google/
{
  "id_token": "eyJhbGciOi..."    // Token de Google
}
```

### Refresh Token

```bash
POST /api/users/refresh/
{
  "refresh": "eyJhbGciOi..."
}
```

### Logout

```bash
POST /api/users/logout/
{
  "refresh": "eyJhbGciOi..."
}
```

## 📊 API Endpoints

### Properties
- `GET /api/properties/` - Listar propiedades
- `POST /api/properties/` - Crear propiedad (admin)
- `GET /api/properties/{id}/` - Detalle de propiedad
- `PUT /api/properties/{id}/` - Actualizar propiedad (admin)
- `DELETE /api/properties/{id}/` - Eliminar propiedad (admin)
- `GET /api/properties/available/` - Propiedades disponibles (público)

### Rentals
- `GET /api/rentals/` - Listar alquileres
- `POST /api/rentals/` - Crear alquiler (admin)
- `GET /api/rentals/{id}/` - Detalle de alquiler
- `PUT /api/rentals/{id}/` - Actualizar alquiler (admin)
- `DELETE /api/rentals/{id}/` - Eliminar alquiler (admin)
- `GET /api/rentals/ending_soon/` - Alquileres por vencer

### Finance
- `GET /api/finance/dashboard/` - Dashboard financiero (admin)
- `GET /api/finance/obligations/` - Listar obligaciones
- `POST /api/finance/obligations/` - Crear obligación (admin)
- `POST /api/finance/obligations/{id}/add_payment/` - Agregar pago

### Maintenance
- `GET /api/maintenance/repairs/` - Listar reparaciones
- `POST /api/maintenance/repairs/` - Crear reparación (admin)
- `GET /api/maintenance/ensers/` - Listar enseres

### Emails
- `POST /api/emails/send-email/` - Enviar correo manualmente (admin)

## 📧 Alertas Automáticas

El sistema incluye un comando para enviar alertas automáticas por email sobre:

- **Obligaciones próximas a vencer** → Email a propietarios
- **Rentas próximas a vencer** → Email a inquilinos
- **Pagos de renta pendientes** → Email a inquilinos

### Uso Manual

```bash
# Alertar 5 días antes (default)
python manage.py send_due_alerts

# Alertar 7 días antes
python manage.py send_due_alerts --days 7
```

### Programación Automática

Para que las alertas se envíen automáticamente todos los días:

#### Windows (Programador de Tareas)

1. Ejecuta el archivo `init_production.bat` para inicializar el sistema
2. Usa el archivo `run_alerts.bat` para probar el envío de alertas
3. Programa la tarea siguiendo la **[GUIA_ALERTAS_AUTOMATICAS.md](GUIA_ALERTAS_AUTOMATICAS.md)**

#### Linux (Cron)

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar diariamente a las 8 AM)
0 8 * * * cd /ruta/proyecto && /ruta/venv/bin/python manage.py send_due_alerts
```


### Configuración de Email

**Desarrollo:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Los emails se imprimen en consola.

**Producción:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
# ... ver PRODUCCION_EMAIL_CONFIG.md
```

## 👥 Roles y Permisos

### Admin
- ✅ Acceso completo (CRUD) a todos los recursos
- ✅ Dashboard financiero
- ✅ Gestión de propiedades, alquileres, obligaciones
- ✅ Autenticación solo con Google OAuth

### Cliente
- ✅ Ver sus propios alquileres
- ✅ Ver sus pagos de obligaciones
- ✅ Ver sus reparaciones y enseres
- ✅ Ver propiedades disponibles
- ❌ NO puede crear, editar o eliminar
- ❌ NO puede ver datos de otros clientes

### Invitado
- ❌ Sin acceso a la API

## 🛠️ Desarrollo

### Crear un Tenant

```python
from apps.rentals.models import Tenant

tenant = Tenant.objects.create(
    name="Juan",
    lastname="Pérez",
    email="juan@test.com",
    phone1="3123456789",
    birth_year=1990
)
# Automáticamente se crea un User con:
# - Username: 3123456789
# - Password: 31234567891990
# - Role: cliente
```

### Aplicar Permisos a ViewSets

```python
from apps.users.permissions import IsAdminOrReadOnlyClient

class RentalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnlyClient]
    
    def get_queryset(self):
        queryset = Rental.objects.all()
        
        user_roles = self.request.user.userrole_set.values_list('role__name', flat=True)
        
        if 'cliente' in user_roles:
            # Clientes solo ven sus rentals
            queryset = queryset.filter(tenant__user=self.request.user)
        
        return queryset
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests de una app específica
python manage.py test apps.rentals

# Tests con cobertura
coverage run --source='.' manage.py test
coverage report
```

## 📦 Estructura del Proyecto

```
hr-properties/
├── apps/
│   ├── emails/          # Sistema de correos y alertas
│   ├── finance/         # Obligaciones y pagos
│   ├── maintenance/     # Reparaciones y enseres
│   ├── properties/      # Gestión de propiedades
│   ├── rentals/         # Alquileres y tenants
│   └── users/           # Autenticación y permisos
├── hr_properties/       # Configuración principal
├── media/               # Archivos subidos
├── logs/                # Logs del sistema
├── init_auth.py         # Script de inicialización de auth
├── init_production.bat  # Script de inicialización de producción
├── run_alerts.bat       # Script para ejecutar alertas (Windows)
├── run_alerts.ps1       # Script para ejecutar alertas (PowerShell)
├── manage.py
├── requirements.txt
├── .env.example         # Plantilla de variables de entorno
├── README.md            # Este archivo
├── GUIA_ALERTAS_AUTOMATICAS.md       # Guía de alertas automáticas
├── EXPLICACION_VISUAL_ALERTAS.md     # Explicación visual del sistema

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

```

## 🔧 Tecnologías

- **Django 5.x**: Framework web
- **Django REST Framework**: API REST
- **Simple JWT**: Autenticación JWT
- **Google Auth**: OAuth para admins
- **SQLite**: Base de datos (desarrollo)
- **Django Filters**: Filtrado de queries

## 📝 Notas Importantes

### Señales Automáticas
- Cuando se crea un `Tenant`, automáticamente se crea un `User` con rol `cliente`
- Las credenciales se generan como: `phone1` + `birth_year`

### Seguridad
- Los admins SOLO pueden autenticarse con Google OAuth
- Los emails de admin deben estar en `ADMIN_EMAILS` del `.env`
- Los tokens JWT expiran en 1 hora (access) y 7 días (refresh)

### Dashboard Financiero
- `obligations`: Total de obligaciones pendientes
- `obligations_month`: Obligaciones del mes actual
- `rentals_by_type`: Desglose de alquileres por tipo (monthly/airbnb/daily)

## 🐛 Troubleshooting

### Error: "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Error: "ADMIN_EMAILS not configured"
- Verificar que `.env` tenga la variable
- Verificar que `settings.py` la esté cargando

### Error: "Email not authorized"
- El email no está en `ADMIN_EMAILS`
- Agregar el email al archivo `.env`

## 📄 Licencia

[Especificar licencia]

## 👨‍💻 Autor

HR Properties Team
