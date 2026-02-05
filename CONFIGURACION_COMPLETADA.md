# ✅ Configuración Completada

## 🎉 ¡Sistema de Autenticación Configurado!

Se han completado los siguientes pasos:

---

## ✅ 1. Configuración de `settings.py`

- ✅ Agregado `timedelta` y `os` a imports
- ✅ Agregado `rest_framework_simplejwt` a INSTALLED_APPS
- ✅ Agregado `rest_framework_simplejwt.token_blacklist` a INSTALLED_APPS
- ✅ Configurado `AUTH_USER_MODEL = 'users.User'`
- ✅ Configurado `GOOGLE_OAUTH_CLIENT_ID`
- ✅ Configurado `REST_FRAMEWORK` con autenticación JWT
- ✅ Configurado `SIMPLE_JWT` con tiempos de expiración

---

## ✅ 2. Permisos Aplicados a ViewSets

### **Rentals**:
- ✅ `TenantViewSet`: Solo admins (IsAdminUser)
- ✅ `RentalViewSet`: Admins CRUD + Clientes lectura de sus datos (IsAdminOrReadOnlyClient)
  - Los clientes solo ven sus propios rentals (filtro por tenant__user)

### **Properties**:
- ✅ `PropertyViewSet`: Solo admins (IsAdminUser)

### **Finance**:
- ✅ `ObligationTypeViewSet`: Solo admins (IsAdminUser)
- ✅ `PaymentMethodViewSet`: Solo admins (IsAdminUser)
- ✅ `ObligationViewSet`: Solo admins (IsAdminUser)
- ✅ `DashboardView`: Solo admins (IsAdminUser)

### **Maintenance**:
- ✅ `RepairViewSet`: Solo admins (IsAdminUser)

---

## 🔄 Próximos Pasos CRÍTICOS

### 📦 1. Instalar Dependencias

```bash
pip install djangorestframework-simplejwt google-auth django-filter
```

O desde requirements.txt:

```bash
pip install -r requirements.txt
```

**⚠️ IMPORTANTE**: Este paso es OBLIGATORIO antes de continuar.

---

### 🗄️ 2. Ejecutar Migraciones

Una vez instaladas las dependencias:

```bash
# Crear migraciones para Tenant (birth_year, phone1 unique)
python manage.py makemigrations rentals

# Crear migraciones para JWT token blacklist
python manage.py makemigrations

# Aplicar todas las migraciones
python manage.py migrate
```

---

### 🔑 3. Crear Roles Iniciales

```bash
python init_auth.py
```

Este script:
- ✅ Crea roles (admin, cliente, invitado)
- ✅ Verifica configuraciones
- ✅ Permite crear un tenant de prueba

---

### 🌐 4. Configurar Variables de Entorno

Crear o actualizar archivo `.env` en la raíz:

```env
# Django
SECRET_KEY=django-insecure-=j2fko_+lqf4*+^#ulxd!rvz*+(46$b*1b2&v30-sy%b@s+oxj
DEBUG=True

# Google OAuth - OBTENER DE: https://console.cloud.google.com/
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Admin Emails (separados por comas)
ADMIN_EMAILS=admin@company.com
```

**📝 Cómo obtener Google OAuth Client ID**:
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto o seleccionar uno existente
3. Habilitar **Google+ API**
4. Ir a **Credenciales** → **Crear credenciales** → **ID de cliente OAuth 2.0**
5. Tipo: **Aplicación web**
6. Agregar orígenes: `http://localhost:3000`
7. Copiar el **Client ID**

---

### 🧪 5. Probar el Sistema

#### A. Crear Tenant de Prueba

```bash
python manage.py shell
```

```python
from apps.rentals.models import Tenant

tenant = Tenant.objects.create(
    name="Juan",
    lastname="Pérez",
    email="juan@test.com",
    phone1="3123456789",
    birth_year=1990
)

print(f"✅ Tenant: {tenant.full_name}")
print(f"📱 Username: {tenant.phone1}")
print(f"🔑 Password: {tenant.phone1}{tenant.birth_year}")
# Salida: Password: 31234567891990
exit()
```

#### B. Probar Login

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "3123456789", "password": "31234567891990"}'
```

---

## 📊 Estado Actual

### ✅ Completado:
1. Implementación de vistas de autenticación (LoginView, GoogleLoginView, LogoutView)
2. URLs de autenticación configuradas
3. Permisos personalizados creados (IsAdminUser, IsAdminOrReadOnlyClient)
4. Permisos aplicados a TODOS los ViewSets
5. Señales para auto-crear Users desde Tenants
6. Configuración de settings.py
7. Documentación completa

### ⏳ Pendiente (depende de dependencias):
1. Instalar paquetes: `djangorestframework-simplejwt`, `google-auth`, `django-filter`
2. Ejecutar migraciones
3. Crear roles iniciales
4. Configurar `.env` con Google OAuth
5. Probar sistema completo

---

## 🚀 Cómo Continuar

### Paso 1: Instalar dependencias
```bash
pip install djangorestframework-simplejwt google-auth django-filter
```

### Paso 2: Verificar instalación
```bash
python check_dependencies.py
```

### Paso 3: Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 4: Inicializar autenticación
```bash
python init_auth.py
```

### Paso 5: Iniciar servidor
```bash
python manage.py runserver
```

---

## 📚 Documentación de Referencia

- **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)**: Guía completa de configuración
- **[AUTHENTICATION_IMPLEMENTATION_SUMMARY.md](AUTHENTICATION_IMPLEMENTATION_SUMMARY.md)**: Resumen de implementación
- **[FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)**: Integración con React
- **[NEXT_STEPS.md](NEXT_STEPS.md)**: Pasos detallados pendientes
- **[README.md](README.md)**: Documentación general

---

## 🎯 Endpoints Disponibles

Una vez completados los pasos anteriores:

### Autenticación:
- `POST /api/users/login/` - Login clientes (credenciales)
- `POST /api/users/google/` - Login admins (Google OAuth)
- `POST /api/users/refresh/` - Renovar access token
- `POST /api/users/logout/` - Cerrar sesión

### Dashboard:
- `GET /api/finance/dashboard/` - Estadísticas (solo admins)

### Propiedades:
- `GET /api/properties/` - Listar (solo admins)
- `POST /api/properties/` - Crear (solo admins)

### Rentals:
- `GET /api/rentals/` - Listar (admins: todos, clientes: solo suyos)
- `POST /api/rentals/` - Crear (solo admins)

---

## 💡 Notas Importantes

1. **Señales Automáticas**: Cuando creas un Tenant, automáticamente se crea un User con rol "cliente"
2. **Contraseñas**: Se generan como `phone1 + birth_year`
3. **Google OAuth**: Solo emails en `ADMIN_EMAILS` pueden autenticarse
4. **Tokens JWT**: Expiran en 1 hora (access) y 7 días (refresh)
5. **Filtros**: Los clientes solo ven sus propios datos automáticamente

---

**Fecha**: 2025-02-04  
**Estado**: ⚠️ Esperando instalación de dependencias para continuar
