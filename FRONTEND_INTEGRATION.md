# 🎨 Frontend - Guía de Integración

Ejemplos completos de integración con React para el sistema de autenticación dual.

---

## 📦 1. Instalación de Dependencias

```bash
npm install @react-oauth/google axios react-router-dom
```

---

## ⚙️ 2. Configuración Inicial

### 2.1. Variables de Entorno

Crear `.env.local`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

### 2.2. Configuración de Axios

`src/utils/api.js`:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
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

// Interceptor para refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${process.env.REACT_APP_API_URL}/api/users/refresh/`,
          { refresh: refreshToken }
        );

        localStorage.setItem('access_token', response.data.access);
        
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
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

---

## 🔐 3. Context de Autenticación

`src/context/AuthContext.js`:

```javascript
import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (credentials) => {
    const response = await api.post('/api/users/login/', credentials);
    const { access, refresh, user: userData } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    
    setUser(userData);
    return userData;
  };

  const googleLogin = async (idToken) => {
    const response = await api.post('/api/users/google/', {
      id_token: idToken
    });
    const { access, refresh, user: userData } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/api/users/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.clear();
      setUser(null);
    }
  };

  const isAdmin = () => {
    return user?.roles?.includes('admin');
  };

  const isClient = () => {
    return user?.roles?.includes('cliente');
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      googleLogin,
      logout,
      isAdmin,
      isClient,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

## 🚪 4. Página de Login

`src/pages/Login.js`:

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [tab, setTab] = useState('admin'); // 'admin' o 'client'
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login, googleLogin } = useAuth();

  const handleClientLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ username: phone, password });
      navigate('/client-dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Credenciales inválidas');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async (credentialResponse) => {
    setError('');
    setLoading(true);

    try {
      await googleLogin(credentialResponse.credential);
      navigate('/admin-dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Error al iniciar sesión con Google');
    } finally {
      setLoading(false);
    }
  };

  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <div className="login-container">
        <div className="login-card">
          <h1>HR Properties</h1>
          
          {/* Tabs */}
          <div className="tabs">
            <button
              className={tab === 'admin' ? 'active' : ''}
              onClick={() => setTab('admin')}
            >
              Administrador
            </button>
            <button
              className={tab === 'client' ? 'active' : ''}
              onClick={() => setTab('client')}
            >
              Cliente
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          {/* Admin Login (Google) */}
          {tab === 'admin' && (
            <div className="admin-login">
              <p>Inicia sesión con tu cuenta de Google</p>
              <GoogleLogin
                onSuccess={handleGoogleLogin}
                onError={() => setError('Error al iniciar sesión con Google')}
                text="signin_with"
                shape="rectangular"
                theme="filled_blue"
                size="large"
              />
            </div>
          )}

          {/* Client Login (Credentials) */}
          {tab === 'client' && (
            <div className="client-login">
              <form onSubmit={handleClientLogin}>
                <div className="form-group">
                  <label>Teléfono</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="3123456789"
                    required
                    disabled={loading}
                  />
                </div>

                <div className="form-group">
                  <label>Contraseña</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Teléfono + año de nacimiento"
                    required
                    disabled={loading}
                  />
                </div>

                <button type="submit" disabled={loading}>
                  {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                </button>
              </form>

              <p className="hint">
                💡 Tu contraseña es tu número de teléfono + año de nacimiento
                <br />
                Ejemplo: 31234567891990
              </p>
            </div>
          )}
        </div>
      </div>
    </GoogleOAuthProvider>
  );
};

export default Login;
```

---

## 🛡️ 5. Rutas Protegidas

`src/components/ProtectedRoute.js`:

```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requireAdmin && !isAdmin()) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};

export default ProtectedRoute;
```

`src/App.js`:

```javascript
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import ClientDashboard from './pages/ClientDashboard';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Rutas de Admin */}
          <Route
            path="/admin-dashboard"
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Rutas de Cliente */}
          <Route
            path="/client-dashboard"
            element={
              <ProtectedRoute>
                <ClientDashboard />
              </ProtectedRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

---

## 📊 6. Dashboard de Admin

`src/pages/AdminDashboard.js`:

```javascript
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/finance/dashboard/');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="admin-dashboard">
      <header>
        <h1>Dashboard - Administrador</h1>
        <div className="user-info">
          <img src={user.picture} alt={user.name} />
          <span>{user.name}</span>
          <button onClick={logout}>Cerrar Sesión</button>
        </div>
      </header>

      <div className="stats-grid">
        {/* Alquileres */}
        <div className="stat-card">
          <h3>Alquileres</h3>
          <div className="stat-value">{stats.rentals_by_type.total}</div>
          <div className="stat-breakdown">
            <div>Mensuales: {stats.rentals_by_type.monthly}</div>
            <div>Airbnb: {stats.rentals_by_type.airbnb}</div>
            <div>Diarios: {stats.rentals_by_type.daily}</div>
          </div>
        </div>

        {/* Obligaciones */}
        <div className="stat-card">
          <h3>Obligaciones Totales</h3>
          <div className="stat-value">{stats.obligations.total}</div>
          <div className="stat-breakdown">
            <div>Pagadas: {stats.obligations.paid}</div>
            <div>Por vencer: {stats.obligations.upcoming_due}</div>
            <div>Vencidas: {stats.obligations.overdue}</div>
          </div>
        </div>

        {/* Obligaciones del Mes */}
        <div className="stat-card">
          <h3>Obligaciones del Mes</h3>
          <div className="stat-value">{stats.obligations_month.total}</div>
          <div className="stat-breakdown">
            <div>Pagadas: {stats.obligations_month.paid}</div>
            <div>Pendientes: {stats.obligations_month.pending}</div>
          </div>
        </div>

        {/* Propiedades */}
        <div className="stat-card">
          <h3>Propiedades</h3>
          <div className="stat-value">{stats.properties.total}</div>
          <div className="stat-breakdown">
            <div>Ocupadas: {stats.properties.occupied}</div>
            <div>Disponibles: {stats.properties.available}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
```

---

## 👤 7. Dashboard de Cliente

`src/pages/ClientDashboard.js`:

```javascript
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const ClientDashboard = () => {
  const { user, logout } = useAuth();
  const [rentals, setRentals] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [rentalsRes, paymentsRes] = await Promise.all([
        api.get('/api/rentals/'),
        api.get('/api/finance/payments/'),
      ]);

      setRentals(rentalsRes.data.results || rentalsRes.data);
      setPayments(paymentsRes.data.results || paymentsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="client-dashboard">
      <header>
        <h1>Mi Panel - {user.name}</h1>
        <button onClick={logout}>Cerrar Sesión</button>
      </header>

      {/* Mis Alquileres */}
      <section>
        <h2>Mis Alquileres</h2>
        {rentals.length === 0 ? (
          <p>No tienes alquileres activos</p>
        ) : (
          <div className="rentals-grid">
            {rentals.map((rental) => (
              <div key={rental.id} className="rental-card">
                <h3>{rental.property_name}</h3>
                <p>Tipo: {rental.rental_type}</p>
                <p>Check-in: {new Date(rental.check_in).toLocaleDateString()}</p>
                <p>Check-out: {new Date(rental.check_out).toLocaleDateString()}</p>
                <p>Precio: ${rental.price}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Mis Pagos */}
      <section>
        <h2>Mis Pagos</h2>
        {payments.length === 0 ? (
          <p>No tienes pagos registrados</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Concepto</th>
                <th>Monto</th>
                <th>Método</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment) => (
                <tr key={payment.id}>
                  <td>{new Date(payment.payment_date).toLocaleDateString()}</td>
                  <td>{payment.obligation_name}</td>
                  <td>${payment.payment_amount}</td>
                  <td>{payment.payment_method}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
};

export default ClientDashboard;
```

---

## 🎨 8. Estilos CSS

`src/styles/Login.css`:

```css
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-card h1 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tabs button {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 5px;
  transition: all 0.3s;
}

.tabs button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.error {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  text-align: center;
}

.admin-login {
  text-align: center;
}

.admin-login p {
  margin-bottom: 1rem;
  color: #666;
}

.client-login .form-group {
  margin-bottom: 1rem;
}

.client-login label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.client-login input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.client-login input:focus {
  outline: none;
  border-color: #667eea;
}

.client-login button {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.client-login button:hover {
  background: #5568d3;
}

.client-login button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.hint {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f0f4ff;
  border-radius: 5px;
  font-size: 0.875rem;
  color: #666;
  text-align: center;
}
```

---

## 🔄 9. Hook Personalizado para API

`src/hooks/useApi.js`:

```javascript
import { useState, useEffect } from 'react';
import api from '../utils/api';

export const useApi = (url, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, dependencies);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.get(url);
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data || 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch: fetchData };
};
```

Uso:

```javascript
const MyComponent = () => {
  const { data, loading, error, refetch } = useApi('/api/rentals/');

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {data.map(item => <div key={item.id}>{item.name}</div>)}
      <button onClick={refetch}>Recargar</button>
    </div>
  );
};
```

---

## ✅ Checklist de Implementación

- [ ] Instalar dependencias (`@react-oauth/google`, `axios`)
- [ ] Configurar `.env.local` con API_URL y GOOGLE_CLIENT_ID
- [ ] Crear `src/utils/api.js` con interceptores
- [ ] Crear `src/context/AuthContext.js`
- [ ] Envolver App con `AuthProvider`
- [ ] Crear página de Login con ambos métodos
- [ ] Crear componente `ProtectedRoute`
- [ ] Configurar rutas en App.js
- [ ] Crear dashboards (Admin y Cliente)
- [ ] Agregar estilos CSS
- [ ] Probar login de admin (Google)
- [ ] Probar login de cliente (credenciales)
- [ ] Probar refresh de tokens
- [ ] Probar logout

---

## 🐛 Troubleshooting

### Error: "Google is not defined"
- Verificar que `GoogleOAuthProvider` envuelve el componente
- Verificar que `REACT_APP_GOOGLE_CLIENT_ID` esté definido

### Token expirado
- El interceptor de Axios debería manejarlo automáticamente
- Verificar que `refresh_token` esté en localStorage

### CORS Error
- Agregar `http://localhost:3000` a CORS en Django
- En `settings.py`: `CORS_ALLOWED_ORIGINS = ['http://localhost:3000']`

---

## 📚 Referencias

- [React OAuth Google](https://www.npmjs.com/package/@react-oauth/google)
- [Axios](https://axios-http.com/)
- [React Router](https://reactrouter.com/)
