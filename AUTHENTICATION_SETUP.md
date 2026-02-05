# 🔐 Sistema de Autenticación - Configuración Completa

Este documento detalla la configuración necesaria para implementar el sistema de autenticación dual:
- **Admins**: Autenticación con Google OAuth
- **Clientes**: Autenticación con credenciales (teléfono + año de nacimiento)

---

## 📦 1. Instalación de Dependencias

```bash
pip install djangorestframework-simplejwt
pip install google-auth
```

Agregar a `requirements.txt`:
```
djangorestframework-simplejwt==5.3.0
google-auth==2.23.0
```

---

## ⚙️ 2. Configuración de `settings.py`

### 2.1. Agregar Apps Instaladas

```python
INSTALLED_APPS = [
    # ... otras apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # Para logout
    # ... apps del proyecto
]
```

### 2.2. Configurar REST Framework

```python
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 2.3. Configurar Simple JWT

```python
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
```

### 2.4. Agregar Google OAuth Client ID

```python
import os

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
```

---

## 🔑 3. Configuración del Archivo `.env`

Crear o actualizar el archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# Admin Emails (separados por comas)
ADMIN_EMAILS=admin1@company.com,admin2@company.com,admin3@company.com
```

### 3.1. Obtener Google OAuth Client ID

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar **Google+ API**
4. Ir a **Credenciales** → **Crear credenciales** → **ID de cliente de OAuth 2.0**
5. Tipo de aplicación: **Aplicación web**
6. Agregar orígenes autorizados:
   - http://localhost:3000 (desarrollo)
   - https://tudominio.com (producción)
7. Copiar el **Client ID** y pegarlo en `.env`

---

## 🗄️ 4. Migrar la Base de Datos

Los siguientes modelos necesitan migración:

### 4.1. Crear Migraciones

```bash
python manage.py makemigrations rentals
```

Esto creará migración para:
- `Tenant.birth_year` (nuevo campo)
- `Tenant.phone1` (ahora es unique)

### 4.2. Aplicar Migraciones

```bash
python manage.py migrate
```

Esto aplicará:
- Migración de `rentals` (Tenant)
- Migración de `simplejwt` (token blacklist)

---

## 👥 5. Crear Roles Iniciales

Ejecutar en shell de Django:

```bash
python manage.py shell
```

```python
from apps.users.models import Role

# Crear roles si no existen
Role.objects.get_or_create(name='admin')
Role.objects.get_or_create(name='cliente')
Role.objects.get_or_create(name='invitado')

print("✅ Roles creados correctamente")
```

---

## 🔗 6. Configurar URLs Principales

Actualizar `hr_properties/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/users/', include('apps.users.urls')),        # 🆕 Autenticación
    path('api/properties/', include('apps.properties.urls')),
    path('api/rentals/', include('apps.rentals.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/maintenance/', include('apps.maintenance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🧪 7. Probar la Autenticación

### 7.1. Crear un Tenant de Prueba

```bash
python manage.py shell
```

```python
from apps.rentals.models import Tenant

tenant = Tenant.objects.create(
    name="Juan Pérez",
    email="juan@example.com",
    phone1="3123456789",
    birth_year=1990
)

print(f"✅ Tenant creado: {tenant.name}")
print(f"📱 Username: {tenant.phone1}")
print(f"🔑 Password: {tenant.phone1}{tenant.birth_year}")
```

La señal automáticamente creará un `User` con:
- Username: `3123456789`
- Password: `31234567891990`
- Role: `cliente`

### 7.2. Probar Login de Cliente

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "3123456789",
    "password": "31234567891990"
  }'
```

Respuesta esperada:
```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi...",
  "user": {
    "id": 1,
    "email": "juan@example.com",
    "name": "Juan Pérez",
    "roles": ["cliente"]
  }
}
```

### 7.3. Crear Admin de Prueba

```bash
python manage.py shell
```

```python
from apps.users.models import User, Role, UserRole

# Crear usuario admin
admin = User.objects.create_user(
    username="admin",
    email="admin@company.com",  # Debe estar en ADMIN_EMAILS del .env
    password="admin123",
    name="Admin User"
)

# Asignar rol admin
admin_role = Role.objects.get(name='admin')
UserRole.objects.create(user=admin, role=admin_role)

print(f"✅ Admin creado: {admin.email}")
```

---

## 🎨 8. Integración con Frontend

### 8.1. Instalar Dependencias (React)

```bash
npm install @react-oauth/google axios
```

### 8.2. Configurar Google OAuth Provider

```javascript
// src/App.js
import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <YourApp />
    </GoogleOAuthProvider>
  );
}
```

### 8.3. Login con Google (Admins)

```javascript
// src/components/GoogleLoginButton.js
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

function GoogleLoginButton() {
  const handleGoogleLogin = async (credentialResponse) => {
    try {
      const response = await axios.post('http://localhost:8000/api/users/google/', {
        id_token: credentialResponse.credential
      });
      
      // Guardar tokens
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Redirigir al dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Login failed:', error.response?.data);
      alert('Error: ' + (error.response?.data?.error || 'Login failed'));
    }
  };

  return (
    <GoogleLogin
      onSuccess={handleGoogleLogin}
      onError={() => console.log('Login Failed')}
      text="signin_with"
      shape="rectangular"
      theme="filled_blue"
    />
  );
}
```

### 8.4. Login con Credenciales (Clientes)

```javascript
// src/components/ClientLoginForm.js
import { useState } from 'react';
import axios from 'axios';

function ClientLoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleClientLogin = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post('http://localhost:8000/api/users/login/', {
        username,
        password
      });
      
      // Guardar tokens
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Redirigir al perfil del cliente
      window.location.href = '/client-dashboard';
    } catch (error) {
      console.error('Login failed:', error.response?.data);
      alert('Error: ' + (error.response?.data?.error || 'Credenciales inválidas'));
    }
  };

  return (
    <form onSubmit={handleClientLogin}>
      <input
        type="text"
        placeholder="Teléfono"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Iniciar Sesión</button>
    </form>
  );
}
```

### 8.5. Configurar Axios con Token

```javascript
// src/utils/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Interceptor para agregar token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://localhost:8000/api/users/refresh/', {
          refresh: refreshToken
        });

        localStorage.setItem('access_token', response.data.access);
        
        // Reintentar petición original
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token expiró, hacer logout
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### 8.6. Logout

```javascript
// src/utils/auth.js
import api from './api';

export const logout = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
      await api.post('/api/users/logout/', {
        refresh: refreshToken
      });
    }
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Limpiar storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Redirigir al login
    window.location.href = '/login';
  }
};
```

---

## 🔒 9. Aplicar Permisos a ViewSets

### 9.1. Rentals (Clientes ven solo sus rentals)

```python
# apps/rentals/views.py
from apps.users.permissions import IsAdminOrReadOnlyClient

class RentalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnlyClient]
    
    def get_queryset(self):
        queryset = Rental.objects.all()
        
        # Filtrar por rol
        user_roles = self.request.user.userrole_set.values_list('role__name', flat=True)
        
        if 'cliente' in user_roles:
            # Clientes solo ven sus propios rentals
            queryset = queryset.filter(tenant__user=self.request.user)
        
        return queryset
```

### 9.2. Properties (Solo admins pueden modificar)

```python
# apps/properties/views.py
from apps.users.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # Solo admins
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available(self, request):
        """Endpoint público para ver propiedades disponibles"""
        properties = Property.objects.filter(rentals__status='available')
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)
```

### 9.3. Finance (Solo admins)

```python
# apps/finance/views.py
from apps.users.permissions import IsAdminUser

class DashboardView(APIView):
    permission_classes = [IsAdminUser]  # Solo admins ven dashboard
    
    def get(self, request):
        # ... código del dashboard
```

---

## ✅ 10. Checklist de Implementación

- [ ] Instalar `djangorestframework-simplejwt` y `google-auth`
- [ ] Configurar `settings.py` (INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT)
- [ ] Configurar `.env` (GOOGLE_OAUTH_CLIENT_ID, ADMIN_EMAILS)
- [ ] Obtener Google OAuth Client ID de Google Cloud Console
- [ ] Ejecutar `makemigrations` para Tenant.birth_year
- [ ] Ejecutar `migrate` para aplicar cambios
- [ ] Crear roles iniciales (admin, cliente, invitado)
- [ ] Actualizar `urls.py` principal para incluir `apps.users.urls`
- [ ] Aplicar permisos a ViewSets (RentalViewSet, PropertyViewSet, etc.)
- [ ] Probar login de cliente con tenant de prueba
- [ ] Probar login de admin con Google OAuth
- [ ] Implementar frontend con Google OAuth Provider
- [ ] Configurar interceptores de Axios para manejo de tokens

---

## 📝 11. Notas Importantes

### Creación Automática de Usuarios
- Cuando se crea un `Tenant`, automáticamente se crea un `User` con:
  - Username: `phone1`
  - Password: `phone1 + birth_year`
  - Role: `cliente`
- Esto se hace mediante una señal en `apps/rentals/signals.py`

### Roles y Permisos
- **admin**: Acceso completo (CRUD) a todos los recursos
- **cliente**: Solo lectura de sus propios datos (rentals, pagos, reparaciones)
- **invitado**: Sin acceso a la API

### Google OAuth
- Solo emails en `ADMIN_EMAILS` pueden hacer login con Google
- El backend verifica el token directamente con Google
- No se requiere django-allauth

### Tokens JWT
- Access Token: 1 hora de vida
- Refresh Token: 7 días de vida
- Los refresh tokens se invalidan al hacer logout (blacklist)

---

## 🐛 12. Troubleshooting

### Error: "ADMIN_EMAILS not configured"
- Asegurarse de que `.env` tenga `ADMIN_EMAILS=email1@domain.com,email2@domain.com`
- Verificar que `settings.py` cargue la variable: `os.getenv('ADMIN_EMAILS')`

### Error: "Email not authorized"
- El email del usuario de Google no está en `ADMIN_EMAILS`
- Agregar el email al archivo `.env`

### Error: "User matching query does not exist"
- El Tenant no tiene un User asociado
- Asegurarse de que la señal está registrada en `apps.py`
- Crear el User manualmente o recrear el Tenant

### Error: "Invalid token"
- El Google ID token es inválido o expiró
- Verificar que `GOOGLE_OAUTH_CLIENT_ID` sea correcto
- El frontend debe obtener un token fresco de Google

---

## 📚 13. Referencias

- [Django REST Framework Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [React OAuth Google](https://www.npmjs.com/package/@react-oauth/google)
