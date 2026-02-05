# ⚡ Pasos Pendientes - Configuración Final

## 🎯 Resumen

Se ha implementado el sistema de autenticación dual completo. Los siguientes pasos son necesarios para completar la configuración.

---

## 📋 Pasos a Seguir

### 1️⃣ Instalar Dependencias

```bash
pip install djangorestframework-simplejwt google-auth django-filter
```

O desde requirements.txt:

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Configurar `settings.py`

Agregar al final de `hr_properties/settings.py`:

```python
from datetime import timedelta
import os

# ==============================
# AUTENTICACIÓN
# ==============================

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Agregar a INSTALLED_APPS (al principio del archivo)
INSTALLED_APPS = [
    # ... apps existentes
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # Para logout
    # ... resto de apps
]
```

**⚠️ Importante**: Asegurarse de que `rest_framework` y las apps de JWT estén en `INSTALLED_APPS`.

---

### 3️⃣ Configurar `.env`

Crear o actualizar el archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-secret-key-actual
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# Admin Emails (separados por comas, sin espacios)
ADMIN_EMAILS=admin1@company.com,admin2@company.com,admin3@company.com
```

**📝 Obtener Google OAuth Client ID**:
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto o seleccionar uno existente
3. Habilitar **Google+ API**
4. Ir a **Credenciales** → **Crear credenciales** → **ID de cliente OAuth 2.0**
5. Tipo: **Aplicación web**
6. Orígenes autorizados:
   - `http://localhost:3000` (desarrollo)
   - Tu dominio de producción
7. Copiar el **Client ID** y pegarlo en `.env`

---

### 4️⃣ Ejecutar Migraciones

```bash
# Crear migraciones para Tenant (birth_year, phone1 unique)
python manage.py makemigrations rentals

# Aplicar todas las migraciones
python manage.py migrate
```

**💡 Nota**: Si ya hay Tenants en la base de datos, Django preguntará por un valor por defecto para `birth_year`. Puedes usar `1990` como valor temporal y luego actualizar manualmente cada tenant.

---

### 5️⃣ Inicializar Sistema de Autenticación

```bash
python init_auth.py
```

Este script:
- ✅ Crea roles (admin, cliente, invitado)
- ✅ Verifica configuraciones
- ✅ Permite crear un tenant de prueba

---

### 6️⃣ Crear Admin de Prueba (Opcional)

Si quieres un usuario admin para pruebas locales:

```bash
python manage.py shell
```

```python
from apps.users.models import User, Role, UserRole

# Crear usuario admin
admin = User.objects.create_user(
    username="admin",
    email="admin@company.com",  # Debe estar en ADMIN_EMAILS
    password="admin123",
    name="Admin User"
)

# Asignar rol admin
admin_role = Role.objects.get(name='admin')
UserRole.objects.create(user=admin, role=admin_role)

print(f"✅ Admin creado: {admin.email}")
exit()
```

---

### 7️⃣ Aplicar Permisos a ViewSets

Actualizar los siguientes archivos para agregar permisos:

#### `apps/rentals/views.py`

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

#### `apps/properties/views.py`

```python
from apps.users.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available(self, request):
        """Propiedades disponibles - acceso público"""
        properties = Property.objects.filter(rentals__status='available')
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)
```

#### `apps/finance/views.py`

```python
from apps.users.permissions import IsAdminUser

class DashboardView(APIView):
    permission_classes = [IsAdminUser]  # Solo admins
    # ... resto del código
```

---

### 8️⃣ Probar Autenticación

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

#### B. Probar Login de Cliente

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "3123456789", "password": "31234567891990"}'
```

Respuesta esperada:

```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi...",
  "user": {
    "id": 1,
    "email": "juan@test.com",
    "name": "Juan",
    "roles": ["cliente"]
  }
}
```

#### C. Probar Endpoint Protegido

```bash
# Usar el access token de la respuesta anterior
curl -X GET http://localhost:8000/api/rentals/ \
  -H "Authorization: Bearer eyJhbGciOi..."
```

---

### 9️⃣ (Opcional) Configurar CORS para Frontend

Si vas a usar un frontend en React, agregar CORS:

```bash
pip install django-cors-headers
```

En `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Al principio
    # ... resto de middleware
]

# Para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Para producción (ajustar según tu dominio)
# CORS_ALLOWED_ORIGINS = [
#     "https://tudominio.com",
# ]
```

---

## ✅ Checklist Final

- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `settings.py` configurado (INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT)
- [ ] `.env` creado con GOOGLE_OAUTH_CLIENT_ID y ADMIN_EMAILS
- [ ] Migraciones ejecutadas (`makemigrations` + `migrate`)
- [ ] Roles creados (`python init_auth.py`)
- [ ] Permisos aplicados a ViewSets
- [ ] Tenant de prueba creado
- [ ] Login de cliente probado
- [ ] (Opcional) Admin de prueba creado
- [ ] (Opcional) CORS configurado para frontend

---

## 🎉 Listo para Usar

Una vez completados estos pasos:

1. **Backend**: Todos los endpoints de autenticación funcionarán
2. **Roles**: Los permisos estarán aplicados correctamente
3. **Señales**: Los Users se crearán automáticamente al crear Tenants
4. **Frontend**: Listo para integrar con React/Vue/Angular

---

## 📚 Documentación de Referencia

- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Guía completa de configuración
- [AUTHENTICATION_IMPLEMENTATION_SUMMARY.md](AUTHENTICATION_IMPLEMENTATION_SUMMARY.md) - Resumen de implementación
- [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) - Integración con React
- [apps/users/urls.py](apps/users/urls.py) - Endpoints disponibles
- [apps/users/permissions.py](apps/users/permissions.py) - Permisos y ejemplos

---

## 🐛 Problemas Comunes

### Error: "No module named 'rest_framework_simplejwt'"

```bash
pip install djangorestframework-simplejwt
```

### Error: "ADMIN_EMAILS not configured"

Verificar que `.env` tenga la variable y que `settings.py` la cargue:

```python
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
```

### Error al crear migración

Si ya hay Tenants sin `birth_year`, Django pedirá un valor por defecto. Usar `1990` y luego actualizar manualmente.

### Token no funciona

Verificar que:
1. El token esté en el header: `Authorization: Bearer <token>`
2. El token no haya expirado (1 hora de vida)
3. El usuario tenga los permisos correctos

---

**Fecha**: 2025-02-01  
**Desarrollado por**: Monitoria HR Properties
