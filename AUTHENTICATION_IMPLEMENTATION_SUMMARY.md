# 📋 Resumen de Implementación - Sistema de Autenticación

## ✅ Archivos Creados/Modificados

### 1. **apps/rentals/models.py** ✅
- ✅ Campo `birth_year` agregado a modelo `Tenant`
- ✅ Campo `phone1` marcado como `unique=True`
- 📝 Documentación sobre generación de contraseñas

### 2. **apps/rentals/signals.py** ✅ (NUEVO)
- ✅ Señal `post_save` para crear automáticamente un `User` cuando se crea un `Tenant`
- ✅ Generación automática de credenciales:
  - Username: `phone1`
  - Password: `phone1 + birth_year`
- ✅ Asignación automática del rol `cliente`

### 3. **apps/rentals/apps.py** ✅
- ✅ Método `ready()` actualizado para registrar las señales

### 4. **apps/users/views.py** ✅ (REESCRITO COMPLETO)
- ✅ `LoginView`: Autenticación con credenciales para clientes
- ✅ `GoogleLoginView`: Autenticación con Google OAuth para admins
- ✅ `LogoutView`: Invalidación de tokens JWT
- ✅ Verificación de emails de admin desde variable de entorno
- ✅ Generación de tokens JWT

### 5. **apps/users/urls.py** ✅
- ✅ Ruta `/login/` - Login con credenciales
- ✅ Ruta `/google/` - Login con Google
- ✅ Ruta `/refresh/` - Renovar access token
- ✅ Ruta `/logout/` - Cerrar sesión
- 📝 Documentación completa de endpoints

### 6. **apps/users/permissions.py** ✅ (NUEVO)
- ✅ `IsAdminUser`: Solo usuarios con rol admin
- ✅ `IsClientUser`: Solo usuarios con rol cliente
- ✅ `IsAdminOrReadOnlyClient`: Admins todo, clientes solo lectura
- 📝 Documentación de uso y ejemplos

### 7. **AUTHENTICATION_SETUP.md** ✅ (NUEVO)
- ✅ Guía completa de configuración
- ✅ Instrucciones de instalación
- ✅ Configuración de settings.py
- ✅ Configuración de .env
- ✅ Creación de roles iniciales
- ✅ Ejemplos de integración con frontend (React)
- ✅ Troubleshooting común

---

## 📦 Dependencias a Instalar

```bash
pip install djangorestframework-simplejwt google-auth django-filter
```

Agregar a `requirements.txt`:
```
djangorestframework-simplejwt==5.3.0
google-auth==2.23.0
django-filter==24.2
```

---

## ⚙️ Configuración Pendiente

### 1. **settings.py**

Agregar al final del archivo:

```python
from datetime import timedelta
import os

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
}

# Agregar a INSTALLED_APPS
INSTALLED_APPS += [
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]
```

### 2. **.env**

Crear o actualizar:

```env
GOOGLE_OAUTH_CLIENT_ID=tu-client-id.apps.googleusercontent.com
ADMIN_EMAILS=admin1@company.com,admin2@company.com
```

### 3. **hr_properties/urls.py**

Verificar que incluya:

```python
urlpatterns = [
    # ...
    path('api/users/', include('apps.users.urls')),
    # ...
]
```

---

## 🗄️ Migraciones Pendientes

### Comando a ejecutar:

```bash
# 1. Crear migraciones
python manage.py makemigrations rentals

# 2. Aplicar migraciones
python manage.py migrate

# 3. Verificar que se aplicaron
python manage.py showmigrations rentals
```

### Cambios que se migrarán:
- ✅ `Tenant.birth_year` (nuevo campo IntegerField)
- ✅ `Tenant.phone1` (unique=True)

---

## 👥 Crear Roles Iniciales

Ejecutar en Django shell:

```bash
python manage.py shell
```

```python
from apps.users.models import Role

Role.objects.get_or_create(name='admin')
Role.objects.get_or_create(name='cliente')
Role.objects.get_or_create(name='invitado')

print("✅ Roles creados")
exit()
```

---

## 🧪 Probar la Implementación

### 1. Crear un Tenant de Prueba

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
```

Esto creará automáticamente un `User` con:
- Username: `3123456789`
- Password: `31234567891990`
- Role: `cliente`

### 2. Probar Login

```bash
# Con curl
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

---

## 🔒 Aplicar Permisos a ViewSets

### Ejemplo: RentalViewSet

```python
# apps/rentals/views.py
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

### ViewSets que necesitan permisos:

- [ ] **RentalViewSet**: `IsAdminOrReadOnlyClient` + filtro por tenant
- [ ] **PropertyViewSet**: `IsAdminUser` (excepto `available` action)
- [ ] **PropertyPaymentViewSet**: `IsAdminOrReadOnlyClient` + filtro
- [ ] **RepairViewSet**: `IsAdminOrReadOnlyClient` + filtro
- [ ] **EnserViewSet**: `IsAdminOrReadOnlyClient` + filtro
- [ ] **PropertyMediaViewSet**: `IsAdminOrReadOnlyClient` + filtro
- [ ] **DashboardView**: `IsAdminUser`

---

## 📱 Frontend - Integración

### Instalar dependencias:

```bash
npm install @react-oauth/google axios
```

### Configurar variables de entorno (.env.local):

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
```

### Ejemplo de uso completo:

Ver archivo [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) sección 8 para ejemplos detallados de:
- Google OAuth Provider setup
- Login con Google (Admins)
- Login con credenciales (Clientes)
- Configuración de Axios con interceptores
- Manejo de refresh tokens
- Logout

---

## 🎯 Próximos Pasos

1. **Instalar dependencias**:
   ```bash
   pip install djangorestframework-simplejwt google-auth django-filter
   ```

2. **Configurar settings.py**:
   - Agregar INSTALLED_APPS
   - Configurar REST_FRAMEWORK
   - Configurar SIMPLE_JWT
   - Agregar GOOGLE_OAUTH_CLIENT_ID

3. **Configurar .env**:
   - GOOGLE_OAUTH_CLIENT_ID
   - ADMIN_EMAILS

4. **Ejecutar migraciones**:
   ```bash
   python manage.py makemigrations rentals
   python manage.py migrate
   ```

5. **Crear roles iniciales**:
   ```bash
   python manage.py shell
   # Ejecutar código de creación de roles
   ```

6. **Probar autenticación**:
   - Crear tenant de prueba
   - Probar login con credenciales
   - Probar login con Google

7. **Aplicar permisos a ViewSets**

8. **Implementar frontend**

---

## 📝 Notas Importantes

### ⚠️ Seguridad

- Las contraseñas se generan automáticamente como `phone1 + birth_year`
- Los admins SOLO pueden autenticarse con Google OAuth
- Los emails de admin deben estar en la variable `ADMIN_EMAILS` del .env
- Los tokens JWT tienen una vida útil de 1 hora (access) y 7 días (refresh)

### 🔄 Señales

- La creación de `User` es automática cuando se crea un `Tenant`
- Si un Tenant ya existe, debes crear el User manualmente
- La señal solo se dispara en operaciones `CREATE`, no en `UPDATE`

### 👥 Roles

- **admin**: Acceso completo a todo
- **cliente**: Solo lectura de sus propios datos
- **invitado**: Sin acceso a la API

---

## 🐛 Troubleshooting

### Error: "No module named 'django_filters'"
```bash
pip install django-filter
```

### Error: "No module named 'rest_framework_simplejwt'"
```bash
pip install djangorestframework-simplejwt
```

### Error: "No module named 'google'"
```bash
pip install google-auth
```

### Error: "ADMIN_EMAILS not configured"
- Verificar que `.env` tenga la variable
- Verificar que `settings.py` la esté cargando con `os.getenv()`

### Error: "Email not authorized" (Google Login)
- El email no está en la lista de `ADMIN_EMAILS`
- Agregar el email al archivo `.env`

### Error al crear migración
- Verificar que el modelo Tenant tenga los campos correctos
- Si ya existen datos, Django preguntará por valor por defecto para `birth_year`

---

## 📚 Documentación Adicional

Para más detalles, consultar:
- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Guía completa de configuración
- [apps/users/urls.py](apps/users/urls.py) - Documentación de endpoints
- [apps/users/permissions.py](apps/users/permissions.py) - Documentación de permisos

---

**Fecha de implementación**: 2025-02-01  
**Desarrollado por**: Monitoria HR Properties
