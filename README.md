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

### Vehicles
#### Endpoints principales

- `GET /api/vehicles/` - Listar vehiculos
- `POST /api/vehicles/` - Crear vehiculo
- `GET /api/vehicles/{id}/` - Detalle de vehiculo
- `PUT /api/vehicles/{id}/` - Actualizar vehiculo completo
- `PATCH /api/vehicles/{id}/` - Actualizar vehiculo parcial
- `DELETE /api/vehicles/{id}/` - Eliminar vehiculo

#### Acciones custom por vehiculo

- `GET /api/vehicles/{id}/documents/` - Listar documentos del vehiculo
- `POST /api/vehicles/{id}/add_document/` - Agregar documento al vehiculo
- `DELETE /api/vehicles/{id}/delete_document/?doc_id={document_id}` - Eliminar documento del vehiculo
- `GET /api/vehicles/{id}/images/` - Listar imagenes del vehiculo
- `POST /api/vehicles/{id}/add_image/` - Agregar imagen al vehiculo
- `DELETE /api/vehicles/{id}/delete_image/?img_id={image_id}` - Eliminar imagen del vehiculo
- `GET /api/vehicles/{id}/responsibles/` - Listar responsables asociados al vehiculo
- `POST /api/vehicles/{id}/add_responsible/` - Asociar responsable existente o crear+asociar
- `POST /api/vehicles/{id}/remove_responsible/` - Desasociar responsable del vehiculo
- `GET /api/vehicles/{id}/repairs/` - Listar reparaciones del vehiculo
- `POST /api/vehicles/{id}/add_repair/` - Crear reparacion del vehiculo
- `GET /api/vehicles/{id}/obligations/` - Listar obligaciones del vehiculo
- `POST /api/vehicles/{id}/add_obligation/` - Crear obligacion del vehiculo
- `GET /api/vehicles/{id}/obligations/{obligation_id}/payments/` - Listar pagos de una obligacion (recomendado)
- `POST /api/vehicles/{id}/obligations/{obligation_id}/payments/` - Registrar pago a una obligacion (recomendado)
- `GET /api/vehicles/{id}/obligation_payments/?obligation_id={obligation_id}` - Listar pagos de una obligacion (compatibilidad)
- `POST /api/vehicles/{id}/add_obligation_payment/` - Registrar pago a una obligacion (compatibilidad)

#### Endpoints CRUD de recursos de vehiculos

- `GET /api/vehicle-documents/`
- `POST /api/vehicle-documents/`
- `GET /api/vehicle-documents/{id}/`
- `PUT/PATCH /api/vehicle-documents/{id}/`
- `DELETE /api/vehicle-documents/{id}/`
- `GET /api/vehicle-images/`
- `POST /api/vehicle-images/`
- `GET /api/vehicle-images/{id}/`
- `PUT/PATCH /api/vehicle-images/{id}/`
- `DELETE /api/vehicle-images/{id}/`
- `GET /api/vehicle-responsibles/`
- `POST /api/vehicle-responsibles/`
- `GET /api/vehicle-responsibles/{id}/`
- `PUT/PATCH /api/vehicle-responsibles/{id}/`
- `DELETE /api/vehicle-responsibles/{id}/`
- `GET /api/vehicle-repairs/`
- `POST /api/vehicle-repairs/`
- `GET /api/vehicle-repairs/{id}/`
- `PUT/PATCH /api/vehicle-repairs/{id}/`
- `DELETE /api/vehicle-repairs/{id}/`
- `GET /api/vehicle-obligation-types/`
- `POST /api/vehicle-obligation-types/`
- `GET /api/vehicle-obligation-types/{id}/`
- `PUT/PATCH /api/vehicle-obligation-types/{id}/`
- `DELETE /api/vehicle-obligation-types/{id}/`
- `GET /api/vehicle-obligations/`
- `POST /api/vehicle-obligations/`
- `GET /api/vehicle-obligations/{id}/`
- `PUT/PATCH /api/vehicle-obligations/{id}/`
- `DELETE /api/vehicle-obligations/{id}/`
- `GET /api/vehicle-payments/`
- `POST /api/vehicle-payments/`
- `GET /api/vehicle-payments/{id}/`
- `PUT/PATCH /api/vehicle-payments/{id}/`
- `DELETE /api/vehicle-payments/{id}/`

#### Campos por recurso

- `Vehicle`:
  - `id` (read only)
  - `owner` (string, requerido)
  - `type` (string, requerido): `commercial`, `sport`, `permanent_use`, `water`
  - `purchase_date` (date `YYYY-MM-DD`, requerido)
  - `purchase_price` (decimal string, requerido)
  - `photo` (file image, opcional)
  - `brand` (string, requerido)
  - `model` (string, requerido)
  - `responsible_ids` (array int, write only, opcional)
  - `responsibles`, `documents`, `images`, `repairs`, `obligations` (read only)

- `Responsible`:
  - `id` (read only)
  - `name` (string, requerido)
  - `email` (email, opcional)
  - `number` (string, opcional)

- `VehicleDocument`:
  - `id` (read only)
  - `vehicle` (int, requerido en CRUD directo)
  - `name` (string, requerido)
  - `file` (file, requerido)

- `VehicleImage`:
  - `id` (read only)
  - `vehicle` (int, requerido en CRUD directo)
  - `image` (file image, requerido)

- `VehicleRepair`:
  - `id` (read only)
  - `vehicle` (int, requerido en CRUD directo)
  - `date` (date `YYYY-MM-DD`, requerido)
  - `description` (string, requerido)
  - `cost` (decimal string, requerido)

- `ObligationVehicleType`:
  - `id` (read only)
  - `name` (string, requerido): `tax`, `insurance`

- `ObligationVehicle`:
  - `id` (read only)
  - `vehicle` (int, requerido en CRUD directo)
  - `entity_name` (string, requerido)
  - `obligation_type` (int, opcional)
  - `due_date` (date `YYYY-MM-DD`, requerido)
  - `amount` (decimal string, requerido)
  - `temporality` (string, requerido): `weekly`, `monthly`, `bimonthly`, `quarterly`, `biannual`, `annual`, `one_time`
  - `file` (file, opcional)
  - `payments`, `total_paid`, `pending`, `is_fully_paid` (read only)

- `VehiclePayment`:
  - `id` (read only)
  - `obligation` (int, requerido en CRUD directo)
  - `payment_method` (int, requerido)
  - `date` (date `YYYY-MM-DD`, requerido)
  - `amount` (decimal string, requerido)
  - `voucher` (file, opcional)

#### JSON de ejemplo para frontend

Crear vehiculo - `POST /api/vehicles/`:

```json
{
  "owner": "Inversiones ABC S.A.S",
  "type": "commercial",
  "purchase_date": "2026-01-10",
  "purchase_price": "158000000.00",
  "brand": "Toyota",
  "model": "Hilux",
  "responsible_ids": [2, 4]
}
```

Actualizar responsables del vehiculo - `PATCH /api/vehicles/{id}/`:

```json
{
  "responsible_ids": [2, 5]
}
```

Respuesta detalle vehiculo - `GET /api/vehicles/{id}/`:

```json
{
  "id": 1,
  "owner": "Inversiones ABC S.A.S",
  "type": "commercial",
  "purchase_date": "2026-01-10",
  "purchase_price": "158000000.00",
  "photo": "http://localhost:8000/media/vehicle_temp/photos/photo.jpg",
  "brand": "Toyota",
  "model": "Hilux",
  "documents": [
    {
      "id": 3,
      "vehicle": 1,
      "name": "Tarjeta de propiedad",
      "file": "http://localhost:8000/media/vehicle_None/docs/tarjeta_propiedad.pdf"
    }
  ],
  "images": [
    {
      "id": 7,
      "vehicle": 1,
      "image": "http://localhost:8000/media/vehicle_temp/photos/photo.jpg"
    }
  ],
  "responsibles": [
    {
      "id": 2,
      "name": "Carlos Ruiz",
      "email": "carlos@demo.com",
      "number": "3001112233"
    }
  ],
  "repairs": [
    {
      "id": 1,
      "vehicle": 1,
      "date": "2026-03-15",
      "description": "Cambio de aceite y filtros",
      "cost": "320000.00"
    }
  ],
  "obligations": [
    {
      "id": 10,
      "vehicle": 1,
      "entity_name": "Sura",
      "obligation_type": 2,
      "obligation_type_name": "insurance",
      "due_date": "2026-12-31",
      "amount": "2300000.00",
      "temporality": "annual",
      "file": "http://localhost:8000/media/vehicle_None/docs/poliza_2026.pdf",
      "payments": [
        {
          "id": 21,
          "obligation": 10,
          "payment_method": 1,
          "payment_method_name": "transfer",
          "date": "2026-12-20",
          "amount": "1000000.00",
          "voucher": "http://localhost:8000/media/vehicle_1/payments/comprobante_1.pdf"
        }
      ],
      "total_paid": "1000000.00",
      "pending": "1300000.00",
      "is_fully_paid": false
    }
  ]
}
```

Asociar responsable existente - `POST /api/vehicles/{id}/add_responsible/`:

```json
{
  "responsible_id": 3
}
```

Crear y asociar responsable - `POST /api/vehicles/{id}/add_responsible/`:

```json
{
  "name": "Juan Perez",
  "email": "juan@mail.com",
  "number": "3001234567"
}
```

Desasociar responsable - `POST /api/vehicles/{id}/remove_responsible/`:

```json
{
  "responsible_id": 3
}
```

Agregar documento - `POST /api/vehicles/{id}/add_document/` (`multipart/form-data`):

```json
{
  "name": "SOAT 2026",
  "file": "<archivo.pdf>"
}
```

Agregar imagen - `POST /api/vehicles/{id}/add_image/` (`multipart/form-data`):

```json
{
  "image": "<imagen.jpg>"
}
```

Agregar reparacion - `POST /api/vehicles/{id}/add_repair/`:

```json
{
  "date": "2026-03-15",
  "description": "Cambio de aceite y filtros",
  "cost": "320000.00"
}
```

Crear obligacion del vehiculo - `POST /api/vehicles/{id}/add_obligation/` (`multipart/form-data` si envia `file`):

```json
{
  "entity_name": "Sura",
  "obligation_type": 2,
  "due_date": "2026-12-31",
  "amount": "2300000.00",
  "temporality": "annual",
  "file": "<poliza_2026.pdf>"
}
```

Registrar pago de obligacion - `POST /api/vehicles/{id}/obligations/{obligation_id}/payments/` (`multipart/form-data` si envia `voucher`):

```json
{
  "payment_method": 1,
  "date": "2026-12-20",
  "amount": "1000000.00",
  "voucher": "<comprobante.pdf>"
}
```

Listar pagos de obligacion - `GET /api/vehicles/{id}/obligations/{obligation_id}/payments/`

Respuesta pago exitoso:

```json
{
  "message": "Payment registered successfully",
  "payment": {
    "id": 21,
    "obligation": 10,
    "payment_method": 1,
    "payment_method_name": "transfer",
    "date": "2026-12-20",
    "amount": "1000000.00",
    "voucher": "http://localhost:8000/media/vehicle_1/payments/comprobante_1.pdf"
  },
  "obligation_status": {
    "total_amount": "2300000.00",
    "total_paid": "1000000.00",
    "pending": "1300000.00",
    "is_fully_paid": false
  }
}
```

Respuesta error por sobrepago:

```json
{
  "error": "Payment exceeds the obligation amount",
  "obligation_amount": "2300000.00",
  "already_paid": "2200000.00",
  "pending": "100000.00",
  "attempted": "200000.00"
}
```

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



## 🚨 Migración de monto total en rentas (Producción)

Esta guía aplica si manejas contratos largos (ejemplo: 1 año) con pago mensual.

### Problema que corrige

Si una renta mensual tiene un único monto en el contrato y no existe monto total del contrato,
el sistema puede interpretar erróneamente que ya está "pagada" después del primer pago mensual.

### Objetivo del cambio

1. Mantener el campo `amount` como monto mensual.
2. Agregar `total_amount` en Rental como monto total del contrato.
3. Cambiar la lógica de estado de pago para comparar contra `total_amount`.
4. Poblar `total_amount` en contratos existentes (backfill).

### Plan de despliegue seguro

1. Respaldar base de datos antes de cualquier cambio.
2. Desplegar código con el nuevo campo y la nueva lógica.
3. Ejecutar migraciones.
4. Ejecutar backfill de datos históricos.
5. Validar en API/UI que un contrato anual no quede pagado con el primer mes.

### Paso 1: Migración del esquema

Crear migración para agregar campo en `apps/rentals/models.py`:

```python
# Ejemplo de campo en Rental
total_amount = models.DecimalField(
  max_digits=12,
  decimal_places=2,
  null=True,
  blank=True,
  verbose_name='Total Contract Amount'
)
```

Aplicar:

```bash
python manage.py makemigrations rentals
python manage.py migrate
```

### Paso 2: Backfill de contratos existentes

Ejecutar una vez en producción (Django shell) para rentas mensuales con fechas válidas y `total_amount` vacío:

```bash
python manage.py shell
```

```python
from decimal import Decimal
from apps.rentals.models import Rental

updated = 0

qs = Rental.objects.filter(
  rental_type='monthly',
  check_in__isnull=False,
  check_out__isnull=False,
  total_amount__isnull=True,
)

for rental in qs:
  months = (rental.check_out.year - rental.check_in.year) * 12 + (rental.check_out.month - rental.check_in.month)
  if months <= 0:
    months = 1

  rental.total_amount = Decimal(rental.amount) * months
  rental.save(update_fields=['total_amount'])
  updated += 1

print(f'Rentals actualizados: {updated}')
```

Notas:
- Para contratos con reglas especiales (prorrateos, meses parciales), ajustar manualmente esos casos.
- Si deseas cubrir meses parciales automáticamente, implementar una regla explícita antes del backfill masivo.

### Paso 3: Ajustar lógica de pagado/pendiente

Regla recomendada para rentas mensuales:

- `expected_total = total_amount` (si existe)
- fallback temporal para datos antiguos: `expected_total = amount`
- `total_paid = suma de rental.payments`
- `pending = max(expected_total - total_paid, 0)`
- `is_fully_paid = total_paid >= expected_total`

Importante:
- Actualizar también recordatorios de pago por email para usar `expected_total`.
- Evitar saldo negativo visual aplicando `max(..., 0)`.

### Paso 4: Verificación post despliegue

Validar al menos estos escenarios:

1. Contrato anual de 1000/mes con 1 pago de 1000:
   - Debe quedar pendiente (no pagado).
2. Contrato anual de 1000/mes con 12 pagos de 1000:
   - Debe quedar pagado.
3. Dashboard e ingresos mensuales:
   - Deben seguir usando fechas reales de los pagos.

### Paso 5: Rollback (si algo falla)

1. Revertir despliegue de aplicación a la versión anterior.
2. Restaurar base de datos desde backup.
3. Revisar casos de contratos parciales antes de repetir el backfill.

### Impacto en producción

Sí, el cambio se refleja en producción una vez que:

1. Se despliega el backend nuevo.
2. Se ejecuta migración.
3. Se hace backfill de `total_amount` en rentas existentes.
4. El frontend consume la nueva lógica de pagado/pendiente.

Si falta alguno de esos pasos, seguirás viendo comportamientos inconsistentes.

### Endpoints y JSON de ejemplo (antes vs ahora)

Esta sección documenta los cambios de respuesta en pagos de rentas después de agregar `total_amount`
y ajustar la lógica de validación de sobrepago.

#### 1) Consultar pagos de un rental

Endpoint:

```http
GET /api/rentals/{id}/payments/
```

##### Antes

```json
{
  "count": 3,
  "total_paid": 3000.0,
  "rental": {
    "id": 5,
    "rental_type": "monthly",
    "amount": "1000.00",
    "check_in": "2026-01-01",
    "check_out": "2027-01-01",
    "status": "occupied"
  },
  "payments": [
    {
      "id": 30,
      "amount": "1000.00",
      "date": "2026-03-01"
    }
  ]
}
```

##### Ahora

```json
{
  "count": 3,
  "total_paid": 3000.0,
  "expected_total": 12000.0,
  "pending": 9000.0,
  "is_fully_paid": false,
  "rental": {
    "id": 5,
    "rental_type": "monthly",
    "amount": "1000.00",
    "total_amount": "12000.00",
    "check_in": "2026-01-01",
    "check_out": "2027-01-01",
    "status": "occupied"
  },
  "payments": [
    {
      "id": 30,
      "amount": "1000.00",
      "date": "2026-03-01"
    }
  ]
}
```

Campos nuevos:
- `expected_total`: total esperado del contrato (`total_amount` o fallback a `amount`)
- `pending`: saldo pendiente
- `is_fully_paid`: indica si ya está totalmente pagado

#### 2) Registrar pago en un rental mensual

Endpoint:

```http
POST /api/properties/{property_id}/rentals/{rental_id}/add_payment/
```

Body ejemplo (monthly):

```json
{
  "payment_method": 1,
  "payment_location": "online",
  "date": "2026-04-01",
  "amount": "1000.00"
}
```

##### Antes

```json
{
  "message": "Payment added successfully to rental",
  "payment": {
    "id": 31,
    "rental": 5,
    "payment_method": 1,
    "payment_location": "online",
    "date": "2026-04-01",
    "amount": "1000.00",
    "voucher_url": null
  }
}
```

##### Ahora

```json
{
  "message": "Payment added successfully to rental",
  "payment": {
    "id": 31,
    "rental": 5,
    "payment_method": 1,
    "payment_location": "online",
    "date": "2026-04-01",
    "amount": "1000.00",
    "voucher_url": null
  },
  "rental_status": {
    "expected_total": "12000.00",
    "total_paid": "4000.00",
    "pending": "8000.00",
    "is_fully_paid": false
  }
}
```

#### 3) Registrar pago con sobrepago (monthly o airbnb)

Mismo endpoint:

```http
POST /api/properties/{property_id}/rentals/{rental_id}/add_payment/
```

Respuesta de error (ahora):

```json
{
  "error": "Payment exceeds the rental expected amount",
  "expected_total": "12000.00",
  "already_paid": "11800.00",
  "pending": "200.00",
  "attempted": "500.00"
}
```

#### 4) Caso Airbnb - pago exitoso

Para `rental_type=airbnb`, el endpoint es el mismo:

```http
POST /api/properties/{property_id}/rentals/{rental_id}/add_payment/
```

Body ejemplo (airbnb):

```json
{
  "payment_method": 2,
  "payment_location": "online",
  "date": "2026-06-10",
  "amount": "350.00"
}
```

Respuesta ejemplo (airbnb):

```json
{
  "message": "Airbnb payment registered successfully (Automatic transfer)",
  "payment": {
    "id": 80,
    "rental": 20,
    "payment_method": 2,
    "payment_location": "online",
    "date": "2026-06-10",
    "amount": "350.00",
    "voucher_url": null
  },
  "rental_status": {
    "expected_total": "1400.00",
    "total_paid": "700.00",
    "pending": "700.00",
    "is_fully_paid": false
  }
}
```

Nota Airbnb:
- El mensaje de éxito cambia a texto específico de Airbnb.
- El cálculo de `expected_total/pending/is_fully_paid` se aplica igual.

#### 5) Resumen de cambios para frontend

1. GET ` /api/rentals/{id}/payments/ ` ahora trae estado financiero del contrato.
2. POST ` /api/properties/{property_id}/rentals/{rental_id}/add_payment/ ` ahora devuelve `rental_status`.
3. POST de pagos ahora puede devolver 400 por sobrepago según total esperado.
4. Airbnb mantiene endpoint y formato base, pero con mensaje específico.