# 🔧 Solución de Errores de Google OAuth

## ❌ Errores Detectados

1. **CORS Error**: "The given origin is not allowed for the given client ID"
2. **Cross-Origin-Opener-Policy**: Política bloqueando postMessage
3. **400 Bad Request**: Fallo en `/api/users/google/`

---

## ✅ Soluciones

### 1. Configurar Google Cloud Console

En [Google Cloud Console](https://console.cloud.google.com/):

#### A. Ir a "Credenciales" → Selecciona tu OAuth 2.0 Client ID

#### B. Orígenes JavaScript autorizados:
```
http://localhost:5173
http://127.0.0.1:5173
```

#### C. URIs de redireccionamiento autorizados:
```
http://localhost:5173
http://localhost:5173/login
http://localhost:5173/callback
http://127.0.0.1:8000/
http://localhost:8000/
```

**💡 IMPORTANTE**: Guardar los cambios y esperar 5-10 minutos para que se propaguen.

---

### 2. Reiniciar el Servidor Django

```bash
# Detener el servidor (Ctrl+C)
# Volver a iniciarlo
python manage.py runserver
```

---

### 3. Verificar Frontend

En tu código React, asegúrate de usar el mismo Client ID:

```javascript
import { GoogleOAuthProvider } from '@react-oauth/google';

<GoogleOAuthProvider clientId="291716469992-472gtuev4o3k3h55sv5phb5m394vbh99.apps.googleusercontent.com">
  {/* Tu app */}
</GoogleOAuthProvider>
```

---

### 4. Verificar el Flujo de Login

El código del login debe ser así:

```javascript
import { GoogleLogin } from '@react-oauth/google';

<GoogleLogin
  onSuccess={async (credentialResponse) => {
    try {
      const response = await fetch('http://localhost:8000/api/users/google/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: credentialResponse.credential
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        console.error('Error del servidor:', error);
        throw new Error(error.error || 'Error al iniciar sesión');
      }
      
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirigir al dashboard
      window.location.href = '/admin-dashboard';
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
      alert('Error: ' + error.message);
    }
  }}
  onError={() => {
    console.log('Login Failed');
    alert('Error al iniciar sesión con Google');
  }}
/>
```

---

## 🧪 Probar la Solución

### Paso 1: Limpiar caché del navegador
- Presiona `Ctrl + Shift + Delete`
- Limpia caché y cookies
- Cierra y abre el navegador

### Paso 2: Probar en modo incógnito
- Abre una ventana de incógnito
- Ve a `http://localhost:5173`
- Intenta hacer login con Google

### Paso 3: Verificar logs del servidor
En la terminal donde corre Django, deberías ver:
```
POST /api/users/google/ 200 OK
```

Si ves:
```
POST /api/users/google/ 400 Bad Request
```

Revisa el error específico en la consola de Django.

---

## 🐛 Debug Adicional

### Ver errores del backend:

En `apps/users/views.py`, la clase `GoogleLoginView` debería mostrar errores. Ejecuta:

```bash
python manage.py shell
```

```python
import os
print("GOOGLE_OAUTH_CLIENT_ID:", os.getenv('GOOGLE_CLIENT_ID'))
print("ADMIN_EMAILS:", os.getenv('ADMIN_EMAILS'))
```

Deberías ver:
```
GOOGLE_OAUTH_CLIENT_ID: 291716469992-472gtuev4o3k3h55sv5phb5m394vbh99.apps.googleusercontent.com
ADMIN_EMAILS: juanestebanortizbejarano@gmail.com
```

---

## 📋 Checklist de Verificación

- [ ] En Google Console: Orígenes autorizados incluyen `http://localhost:5173`
- [ ] En Google Console: URIs de redireccionamiento configurados
- [ ] Archivo `.env` tiene `GOOGLE_CLIENT_ID` correcto
- [ ] `ADMIN_EMAILS` en `.env` incluye tu email de Google
- [ ] Servidor Django reiniciado
- [ ] Frontend usa el mismo Client ID
- [ ] CORS configurado en `settings.py`
- [ ] Caché del navegador limpiada

---

## 🎯 Próximos Pasos

Una vez que funcione el login:

1. Verás tu nombre y email en la respuesta
2. Los tokens se guardarán en `localStorage`
3. Serás redirigido al dashboard
4. Todas las peticiones al backend incluirán el token automáticamente

---

## ❓ Si el Error Persiste

### Verificar que el email esté autorizado:

El backend valida que el email esté en `ADMIN_EMAILS`. Si intentas con otro email, verás:

```json
{
  "error": "Email not authorized. Only admin emails can access."
}
```

**Solución**: Agrega el email al `.env`:
```env
ADMIN_EMAILS=email1@gmail.com,email2@gmail.com
```

### Error de token inválido:

```json
{
  "error": "Invalid Google token"
}
```

**Causa**: El token de Google expiró o es inválido.

**Solución**: Refresca la página y vuelve a intentar.

---

**Fecha**: 2026-02-04  
**Estado**: Configuración actualizada - Probar después de reiniciar servidor
