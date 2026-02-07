# 📋 CAMBIOS EN LA API DE PROPIEDADES - GUÍA PARA FRONTEND

## 🎯 Resumen de Cambios

Se han implementado los siguientes cambios importantes en la API:

1. **Acceso público** a propiedades disponibles (sin autenticación)
2. **Ocultamiento de información financiera** para usuarios no autenticados
3. **Eliminación del concepto "active"** - ahora solo se usa **"occupied"** y **"available"**
4. **Soft delete** - Las propiedades eliminadas no aparecen en ninguna consulta

---

## 🔓 ACCESO PÚBLICO (Sin Autenticación)

### ✅ Lo que PUEDEN hacer usuarios anónimos:

#### 1. **Listar propiedades disponibles**
```http
GET /api/properties/?rental_status=available
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Casa en el Centro",
    "use": "rental",
    "address": "Calle 123",
    "map_url": "https://maps.google.com/...",
    "zip_code": "110111",
    "type_building": "house",
    "state": "Cundinamarca",
    "city": "Bogotá",
    "image_url": "/media/properties/casa1.jpg",
    "details": {
      "bedrooms": 3,
      "bathrooms": 2,
      "floors": 2,
      "observations": "Hermosa casa",
      "buildings": 1
    },
    "media": [
      {
        "id": 1,
        "media_type": "image",
        "url": "/media/property_media/foto1.jpg",
        "uploaded_at": "2026-02-05T10:30:00Z"
      }
    ]
  }
]
```

#### 2. **Ver detalles de una propiedad disponible**
```http
GET /api/properties/1/
```

**Solo funciona si la propiedad está disponible (sin rental activo).**

**Respuesta (USUARIO NO AUTENTICADO):**
```json
{
  "id": 1,
  "name": "Casa en el Centro",
  "use": "rental",
  "address": "Calle 123",
  "map_url": "https://maps.google.com/...",
  "zip_code": "110111",
  "type_building": "house",
  "state": "Cundinamarca",
  "city": "Bogotá",
  "image_url": "/media/properties/casa1.jpg",
  "details": {
    "bedrooms": 3,
    "bathrooms": 2,
    "floors": 2,
    "observations": "Hermosa casa",
    "buildings": 1
  },
  "media": [...],
  "inventory": [
    {
      "id": 1,
      "enser": {
        "id": 1,
        "name": "Sofá"
        // ⚠️ NO incluye "price" para usuarios anónimos
      },
      "url_media": "/media/enser_inventory/sofa.jpg"
    }
  ],
  "repairs": [
    {
      "id": 1,
      "date": "2026-01-15",
      "observation": "Reparación de tubería",
      "description": "Se reparó fuga en baño principal"
      // ⚠️ NO incluye "cost" para usuarios anónimos
    }
  ]
  // ⚠️ NO incluye "laws" (regulaciones/documentos legales) para usuarios anónimos
}
```

### ❌ Lo que NO PUEDEN hacer usuarios anónimos:

- ❌ Crear propiedades (POST /api/properties/)
- ❌ Editar propiedades (PUT/PATCH /api/properties/{id}/)
- ❌ Eliminar propiedades (DELETE /api/properties/{id}/)
- ❌ Ver propiedades ocupadas (rental_status=occupied)
- ❌ Ver información financiera (repairs_cost, financials)
- ❌ Ver documentos legales/regulaciones (laws)
- ❌ Ver precios de enseres
- ❌ Ver costos de reparaciones

---

## 🔒 ACCESO ADMIN (Con Autenticación)

### ✅ Lo que PUEDEN hacer administradores:

#### 1. **Listar TODAS las propiedades (con cualquier filtro)**
```http
GET /api/properties/
GET /api/properties/?rental_status=occupied
GET /api/properties/?rental_status=available
GET /api/properties/?rental_status=ending_soon
GET /api/properties/?use=rental
GET /api/properties/?rental_type=monthly,airbnb
```

#### 2. **Ver detalles completos de CUALQUIER propiedad**
```http
GET /api/properties/1/
```

**Respuesta (ADMIN AUTENTICADO):**
```json
{
  "id": 1,
  "name": "Casa en el Centro",
  // ... todos los campos básicos
  "details": {...},
  "media": [...],
  "inventory": [
    {
      "id": 1,
      "enser": {
        "id": 1,
        "name": "Sofá",
        "price": 1500000.00  // ✅ INCLUYE precio
      },
      "url_media": "/media/enser_inventory/sofa.jpg"
    }
  ],
  "repairs": [
    {
      "id": 1,
      "cost": 500000.00,  // ✅ INCLUYE costo
      "date": "2026-01-15",
      "observation": "Reparación de tubería",
      "description": "Se reparó fuga en baño principal"
    }
  ],
  "laws": [  // ✅ INCLUYE documentos legales
    {
      "id": 1,
      "entity_name": "Catastro",
      "url": "/media/property_laws/catastro.pdf",
      "original_amount": 2000000.00,
      "legal_number": "123456",
      "is_paid": true
    }
  ]
}
```

#### 3. **Información financiera**
```http
GET /api/properties/1/repairs_cost/
GET /api/properties/1/financials/
```

#### 4. **Crear, editar, eliminar propiedades**
```http
POST   /api/properties/
PUT    /api/properties/1/
PATCH  /api/properties/1/
DELETE /api/properties/1/
```

---

## 🔄 CAMBIO IMPORTANTE: "active" → "occupied"

### ❌ ANTES (Ya NO usar):
```javascript
// ❌ NO HACER ESTO
fetch('/api/properties/?rental_status=active')
```

### ✅ AHORA (Usar):
```javascript
// ✅ HACER ESTO
fetch('/api/properties/?rental_status=occupied')
```

### 📊 Estados de Propiedades:

| Estado | Descripción | Quién puede ver |
|--------|-------------|-----------------|
| `available` | Propiedad SIN rental activo (disponible para alquilar) | 🌍 Público + 🔒 Admins |
| `occupied` | Propiedad CON rental activo (ocupada) | 🔒 Solo Admins |
| `ending_soon` | Propiedad ocupada cuyo rental termina en ≤30 días | 🔒 Solo Admins |

---

## 🗑️ SOFT DELETE

Las propiedades con `is_deleted != NULL` están marcadas como eliminadas:
- ❌ NO aparecen en listados
- ❌ NO aparecen en conteos
- ❌ NO se consideran para cálculos financieros
- ❌ NO se consideran para dashboard
- ✅ Pueden restaurarse con `POST /api/properties/{id}/restore/`

---

## 🛠️ EJEMPLOS DE USO EN EL FRONTEND

### 1. **Página pública de propiedades disponibles (sin autenticación)**

```javascript
// Listar propiedades disponibles (público)
async function fetchAvailableProperties() {
  const response = await fetch('http://localhost:8000/api/properties/?rental_status=available', {
    method: 'GET',
    // ⚠️ NO se envía token de autenticación
  });
  
  const properties = await response.json();
  return properties;
}

// Ver detalle de una propiedad disponible (público)
async function fetchPropertyDetail(propertyId) {
  const response = await fetch(`http://localhost:8000/api/properties/${propertyId}/`, {
    method: 'GET',
    // ⚠️ NO se envía token de autenticación
  });
  
  if (response.status === 401) {
    // La propiedad está ocupada o no existe
    console.error('Esta propiedad no está disponible públicamente');
    return null;
  }
  
  const property = await response.json();
  // ⚠️ NO tendrá: laws, precios de enseres, costos de reparaciones
  return property;
}
```

### 2. **Dashboard de administrador (con autenticación)**

```javascript
// Listar propiedades ocupadas (solo admin)
async function fetchOccupiedProperties(token) {
  const response = await fetch('http://localhost:8000/api/properties/?rental_status=occupied', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,  // ✅ Token de admin
    }
  });
  
  if (response.status === 401) {
    console.error('No tienes permisos');
    return [];
  }
  
  const properties = await response.json();
  return properties;
}

// Listar propiedades que terminan pronto (solo admin)
async function fetchEndingSoonProperties(token) {
  const response = await fetch('http://localhost:8000/api/properties/?rental_status=ending_soon', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  const properties = await response.json();
  return properties;
}

// Ver información financiera (solo admin)
async function fetchPropertyFinancials(propertyId, token) {
  const response = await fetch(`http://localhost:8000/api/properties/${propertyId}/financials/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  const financials = await response.json();
  // {
  //   income: { rental_payments: 5000000, total_income: 5000000 },
  //   expenses: { obligations: 1200000, repairs: 800000, total_expenses: 2000000 },
  //   balance: 3000000
  // }
  return financials;
}
```

### 3. **Filtros combinados**

```javascript
// Propiedades de tipo rental, disponibles (público)
fetch('/api/properties/?use=rental&rental_status=available')

// Propiedades ocupadas de tipo Airbnb (solo admin)
fetch('/api/properties/?rental_status=occupied&rental_type=airbnb', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// Propiedades que terminan pronto, de tipo mensual (solo admin)
fetch('/api/properties/?rental_status=ending_soon&rental_type=monthly', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

## 📝 CHECKLIST PARA ACTUALIZAR EL FRONTEND

### 1. **Reemplazar "active" por "occupied"**
- [ ] Buscar todas las referencias a `rental_status=active`
- [ ] Reemplazar por `rental_status=occupied`
- [ ] Actualizar labels en la UI: "Activo" → "Ocupado"

### 2. **Implementar página pública de propiedades**
- [ ] Crear ruta pública (sin autenticación) para `/properties`
- [ ] Mostrar solo propiedades con `rental_status=available`
- [ ] NO mostrar información financiera (precios, costos)
- [ ] NO mostrar documentos legales

### 3. **Actualizar dashboard de admin**
- [ ] Usar `rental_status=occupied` para propiedades ocupadas
- [ ] Usar `rental_status=available` para propiedades disponibles
- [ ] Usar `rental_status=ending_soon` para rentals próximos a terminar
- [ ] Asegurarse de enviar token de autenticación en todas las peticiones

### 4. **Manejo de errores**
- [ ] Si usuario anónimo intenta ver propiedad ocupada → 401 Unauthorized
- [ ] Si usuario anónimo intenta crear/editar/eliminar → 401 Unauthorized
- [ ] Si admin intenta ver propiedad eliminada → 404 Not Found

### 5. **Validaciones de UI**
- [ ] Ocultar botones de crear/editar/eliminar para usuarios anónimos
- [ ] Mostrar mensaje "Iniciar sesión para ver más detalles" si es necesario
- [ ] No mostrar precio de enseres en vista pública
- [ ] No mostrar costos de reparaciones en vista pública

---

## ⚠️ IMPORTANTE

### Soft Delete:
Las propiedades con `is_deleted != NULL` **NO aparecen** en:
- ❌ Listados
- ❌ Conteos
- ❌ Dashboard
- ❌ Cálculos financieros

Solo los admins pueden:
- Ver propiedades eliminadas: `GET /api/properties/deleted/`
- Restaurar propiedades: `POST /api/properties/{id}/restore/`

### Rentals:
- ✅ Una propiedad puede tener múltiples rentals en la historia
- ⚠️ Solo puede tener **1 rental activo** (status='occupied') a la vez
- ✅ Cuando un rental está activo, la propiedad pasa a `occupied`
- ✅ Cuando el rental termina (status='available'), la propiedad vuelve a `available`

---

## 🚀 Testing Rápido

```bash
# Probar acceso público (sin autenticación)
curl http://localhost:8000/api/properties/?rental_status=available

# Probar acceso admin (con autenticación)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/properties/?rental_status=occupied

# Probar crear propiedad sin autenticación (debe fallar con 401)
curl -X POST http://localhost:8000/api/properties/ -H "Content-Type: application/json" -d '{...}'
```

---

## 📞 Contacto

Si tienes dudas sobre la implementación, revisa:
- Los comentarios en el código de `views.py`
- Los comentarios en `permissions.py`
- Este documento

✅ **Cambios implementados exitosamente**
