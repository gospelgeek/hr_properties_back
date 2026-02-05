"""
URLs de autenticación
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, GoogleLoginView, LogoutView

urlpatterns = [
    # Autenticación con credenciales (clientes)
    path('login/', LoginView.as_view(), name='login'),
    
    # Autenticación con Google (admins)
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    
    # Refresh token
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
]

'''
═══════════════════════════════════════════════════════════════════════
🔐 AUTENTICACIÓN - ENDPOINTS DISPONIBLES
═══════════════════════════════════════════════════════════════════════

1. LOGIN CLIENTES (Credenciales):
   POST /api/users/login/
   {
     "username": "3123456789",      // phone1 del tenant
     "password": "31234567891990"   // phone1 + birth_year
   }
   
   Respuesta:
   {
     "access": "eyJhbGciOi...",
     "refresh": "eyJhbGciOi...",
     "user": {
       "id": 1,
       "email": "cliente@example.com",
       "name": "Juan Pérez",
       "roles": ["cliente"]
     }
   }

2. LOGIN ADMINS (Google OAuth):
   POST /api/users/google/
   {
     "id_token": "eyJhbGciOi..."    // Token de Google
   }
   
   IMPORTANTE: Solo funciona para emails en ADMIN_EMAILS del .env
   
   Respuesta:
   {
     "access": "eyJhbGciOi...",
     "refresh": "eyJhbGciOi...",
     "user": {
       "id": 2,
       "email": "admin@company.com",
       "name": "Admin User",
       "picture": "https://lh3.googleusercontent.com/...",
       "roles": ["admin"]
     }
   }

3. REFRESH TOKEN:
   POST /api/users/refresh/
   {
     "refresh": "eyJhbGciOi..."
   }
   
   Respuesta:
   {
     "access": "eyJhbGciOi..."
   }

4. LOGOUT:
   POST /api/users/logout/
   {
     "refresh": "eyJhbGciOi..."
   }

═══════════════════════════════════════════════════════════════════════
📋 CONFIGURACIÓN REQUERIDA
═══════════════════════════════════════════════════════════════════════

.env:
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
ADMIN_EMAILS=admin1@company.com,admin2@company.com,admin3@company.com

settings.py:
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')

INSTALLED_APPS += [
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

═══════════════════════════════════════════════════════════════════════
🎨 FRONTEND - INTEGRACIÓN
═══════════════════════════════════════════════════════════════════════

GOOGLE LOGIN:
1. Instalar: npm install @react-oauth/google
2. Configurar Google OAuth Client ID
3. Obtener token de Google
4. Enviar al backend

Ejemplo React:
```javascript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId="your-client-id">
      <GoogleLogin
        onSuccess={async (credentialResponse) => {
          const response = await fetch('/api/users/google/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id_token: credentialResponse.credential
            })
          });
          const data = await response.json();
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
        }}
        onError={() => console.log('Login Failed')}
      />
    </GoogleOAuthProvider>
  );
}
```

CLIENT LOGIN:
```javascript
const handleClientLogin = async (username, password) => {
  const response = await fetch('/api/users/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
};
```

USO DEL TOKEN:
```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```
'''
