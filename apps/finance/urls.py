"""
FINANCE APP - URLs para gestión financiera de propiedades

═══════════════════════════════════════════════════════════════════════
📋 CATÁLOGOS (ViewSets con Router)
═══════════════════════════════════════════════════════════════════════

1. OBLIGATION TYPES (Tipos de obligaciones):
   - GET    /api/obligation-types/          → Listar todos los tipos
   - POST   /api/obligation-types/          → Crear nuevo tipo
   - GET    /api/obligation-types/{id}/     → Ver detalle
   - PUT    /api/obligation-types/{id}/     → Actualizar completo
   - PATCH  /api/obligation-types/{id}/     → Actualizar parcial
   - DELETE /api/obligation-types/{id}/     → Eliminar
   - GET    /api/obligation-types/choices/  → ✨ Obtener opciones disponibles (tax, seguro, cuota)

2. PAYMENT METHODS (Métodos de pago):
   - GET    /api/payment-methods/           → Listar todos
   - POST   /api/payment-methods/           → Crear nuevo
   - GET    /api/payment-methods/{id}/      → Ver detalle
   - PUT    /api/payment-methods/{id}/      → Actualizar completo
   - PATCH  /api/payment-methods/{id}/      → Actualizar parcial
   - DELETE /api/payment-methods/{id}/      → Eliminar

3. OBLIGATIONS (Todas las obligaciones del sistema) ✨ CON FILTROS Y PAGINACIÓN:
   - GET    /api/obligations/               → Listar todas con pagos (paginado)
   - GET    /api/obligations/{id}/          → Ver detalle con pagos
   - PUT    /api/obligations/{id}/          → Actualizar completo
   - PATCH  /api/obligations/{id}/          → Actualizar parcial
   - DELETE /api/obligations/{id}/          → Eliminar
   - GET    /api/obligations/choices/       → ✨ Obtener opciones de temporalidad
   
   FILTROS DISPONIBLES:
   - ?temporality=monthly                   → Por temporalidad
   - ?obligation_type=1                     → Por tipo
   - ?property=2                            → Por propiedad
   - ?due_date_from=2026-02-01              → Fecha desde
   - ?due_date_to=2026-02-28                → Fecha hasta
   - ?amount_min=100000                     → Monto mínimo
   - ?amount_max=500000                     → Monto máximo
   - ?entity_contains=luz                   → Búsqueda parcial
   - ?search=EAAB                           → Búsqueda general
   - ?ordering=-amount                      → Ordenar por monto desc
   - ?ordering=due_date                     → Ordenar por fecha asc
   - ?page=1&page_size=50                   → Paginación
   
   EJEMPLO COMBINADO:
   /api/obligations/?property=2&due_date_from=2026-02-01&ordering=-amount&page=1

═══════════════════════════════════════════════════════════════════════
🏠 OBLIGACIONES POR PROPIEDAD (Nested Resources)
═══════════════════════════════════════════════════════════════════════

4. CREAR OBLIGACIÓN EN PROPIEDAD:
   POST /api/properties/{property_id}/add_obligation/
   Body: {
       "obligation_type": 1,
       "entity_name": "EAAB",
       "amount": 50000,
       "due_date": "2026-02-15",
       "temporality": "monthly"
   }

5. LISTAR OBLIGACIONES DE PROPIEDAD:
   GET /api/properties/{property_id}/obligations/
   → Retorna todas las obligaciones con sus pagos y montos pendientes

6. DETALLE DE OBLIGACIÓN:
   GET    /api/properties/{property_id}/obligations/{obligation_id}/
   PUT    /api/properties/{property_id}/obligations/{obligation_id}/
   PATCH  /api/properties/{property_id}/obligations/{obligation_id}/
   DELETE /api/properties/{property_id}/obligations/{obligation_id}/

═══════════════════════════════════════════════════════════════════════
💳 PAGOS DE OBLIGACIONES (Nested dentro de Obligations)
═══════════════════════════════════════════════════════════════════════

7. CREAR PAGO PARA OBLIGACIÓN:
   POST /api/properties/{property_id}/obligations/{obligation_id}/add_payment/
   Body: {
       "payment_method": 1,
       "amount": 50000,
       "date": "2026-02-01",
       "voucher_url": "https://..."  (opcional)
   }
   → Valida que no se exceda el monto total de la obligación
   → Retorna estado actualizado (total pagado, pendiente, completado)

8. LISTAR PAGOS DE OBLIGACIÓN:
   GET /api/properties/{property_id}/obligations/{obligation_id}/payments/
   → Todos los pagos de una obligación específica

9. DETALLE DE PAGO:
   GET    /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
   PUT    /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
   PATCH  /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
   DELETE /api/properties/{property_id}/obligations/{obligation_id}/payments/{payment_id}/
   
   # 1. Obtener solo propiedades de rental
GET /api/properties/?use=rental

# 2. Ver finanzas de propiedad específica
GET /api/properties/1/financials/

# 3. Ver total de reparaciones
GET /api/properties/1/repairs_cost/

═══════════════════════════════════════════════════════════════════════
📊 DASHBOARD - ESTADÍSTICAS GENERALES
═══════════════════════════════════════════════════════════════════════

10. DASHBOARD:
    GET /api/dashboard/
    
    RESPUESTA:
    {
        "obligations": {
            "total_count": 45,           // Total histórico
            "total_amount": 15000000.00,
            "total_paid": 8500000.00,
            "pending": 6500000.00,
            "upcoming_due": 3            // Vencen en 7 días
        },
        "obligations_month": {
            "total_count": 12,           // Solo del mes actual
            "total_amount": 2500000.00,
            "total_paid": 1200000.00,
            "pending": 1300000.00,
            "upcoming_due": 1            // Del mes que vencen en 7 días
        },
        "properties": {
            "total": 12,
            "by_use": [
                {"use": "rental", "count": 8}
            ]
        },
        "rentals": {
            "active": 6,
            "available": 2,
            "ending_soon": 1,
            "monthly_active": 4,         // Rentals mensuales activos
            "monthly_available": 1,
            "monthly_ending_soon": 1,
            "airbnb_active": 2,          // Rentals Airbnb activos
            "airbnb_available": 1,
            "airbnb_ending_soon": 0
        },
        "monthly_summary": {
            "rental_income": 4500000.00,
            "obligation_payments": 1200000.00,
            "repair_costs": 300000.00,
            "net": 3000000.00
        }
    }
    
    FUNCIONAMIENTO:
    - Calcula estadísticas en tiempo real
    - obligations: Todos los históricos del sistema
    - obligations_month: Solo obligaciones del mes actual
    - upcoming_due: obligaciones que vencen en 7 días
    - ending_soon: rentals que terminan en 30 días
    - monthly_summary: datos del mes actual
    - Útil para mostrar en pantalla principal del sistema

═══════════════════════════════════════════════════════════════════════
🔔 NOTIFICACIONES - SISTEMA DE ALERTAS
═══════════════════════════════════════════════════════════════════════

11. NOTIFICATIONS (ViewSet completo):
    - GET    /api/notifications/                        → Listar no leídas (paginado)
    - GET    /api/notifications/?is_read=true          → Listar todas las leídas
    - GET    /api/notifications/?type=obligation_due   → Filtrar por tipo
    - GET    /api/notifications/?priority=high         → Filtrar por prioridad
    - GET    /api/notifications/{id}/                  → Ver detalle
    - POST   /api/notifications/                       → Crear notificación manual
    - DELETE /api/notifications/{id}/                  → Eliminar
    
    ACCIONES ESPECIALES:
    - POST /api/notifications/{id}/mark_as_read/       → Marcar una como leída
    - POST /api/notifications/mark_all_as_read/        → Marcar todas como leídas
    - GET  /api/notifications/unread_count/            → Contador de no leídas
    
    FILTROS:
    - ?type=obligation_due                             → Por tipo
    - ?priority=high                                   → Por prioridad
    - ?is_read=false                                   → No leídas (default)
    - ?created_from=2026-02-01                         → Desde fecha
    - ?ordering=-created_at                            → Más recientes primero
    
    CREAR NOTIFICACIÓN MANUAL:
    POST /api/notifications/
    {
        "type": "obligation_due",
        "priority": "high",
        "title": "Pago de luz",
        "message": "La obligación de EAAB vence en 3 días",
        "obligation": 1
    }
    
    CONTADOR PARA BADGE:
    GET /api/notifications/unread_count/
    → {"count": 5}
    
    FUNCIONAMIENTO:
    - Por defecto muestra solo notificaciones NO leídas
    - Se pueden crear manualmente o automáticamente (con tareas programadas)
    - Útil para mostrar "campanita" 🔔 en el frontend
    - El contador se puede usar para el badge numérico

═══════════════════════════════════════════════════════════════════════
📊 FLUJO DE TRABAJO COMPLETO
═══════════════════════════════════════════════════════════════════════

1. SETUP INICIAL:
   - POST /api/payment-methods/  → Crear "Transferencia", "Efectivo", etc.
   - POST /api/obligation-types/ → Crear "tax", "seguro", "cuota"

2. GESTIÓN DE OBLIGACIONES:
   - POST /api/properties/2/add_obligation/              → Crear obligación
   - POST /api/properties/2/obligations/1/add_payment/   → Registrar pago
   - GET  /api/properties/2/obligations/                 → Ver todas con estado

3. CONSULTAR DASHBOARD:
   - GET /api/dashboard/  → Ver estadísticas generales

4. GESTIONAR NOTIFICACIONES:
   - GET  /api/notifications/unread_count/               → Ver contador
   - GET  /api/notifications/                            → Ver todas no leídas
   - POST /api/notifications/5/mark_as_read/             → Marcar como leída

5. FILTRADO AVANZADO:
   - GET /api/obligations/?property=2&due_date_from=2026-02-01&ordering=-amount
   - GET /api/notifications/?type=obligation_due&priority=high

═══════════════════════════════════════════════════════════════════════
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ObligationTypeViewSet,
    PaymentMethodViewSet,
    ObligationViewSet,
    PropertyAddObligationView,
    PropertyObligationsListView,
    PropertyObligationDetailView,
    ObligationAddPaymentView,
    ObligationPaymentsListView,
    ObligationPaymentDetailView,
    DashboardView,
    NotificationViewSet,
)

# Router para ViewSets (CRUD completo)
router = DefaultRouter()
router.register(r'obligation-types', ObligationTypeViewSet, basename='obligation-type')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'obligations', ObligationViewSet, basename='obligation')
router.register(r'notifications', NotificationViewSet, basename='notification')

# URLs anidadas dentro de properties
property_patterns = [
    # Crear obligación en propiedad
    path('properties/<int:property_id>/add_obligation/', 
         PropertyAddObligationView.as_view(), 
         name='property-add-obligation'),
    
    # Listar obligaciones de una propiedad
    path('properties/<int:property_id>/obligations/', 
         PropertyObligationsListView.as_view(), 
         name='property-obligations-list'),
    
    # Detalle de obligación específica
    path('properties/<int:property_id>/obligations/<int:obligation_id>/', 
         PropertyObligationDetailView.as_view(), 
         name='property-obligation-detail'),
    
    # Añadir pago a obligación
    path('properties/<int:property_id>/obligations/<int:obligation_id>/add_payment/', 
         ObligationAddPaymentView.as_view(), 
         name='obligation-add-payment'),
    
    # Listar pagos de obligación
    path('properties/<int:property_id>/obligations/<int:obligation_id>/payments/', 
         ObligationPaymentsListView.as_view(), 
         name='obligation-payments-list'),
    
    # Detalle de pago específico
    path('properties/<int:property_id>/obligations/<int:obligation_id>/payments/<int:payment_id>/', 
         ObligationPaymentDetailView.as_view(), 
         name='obligation-payment-detail'),
]

# URLs anidadas dentro de properties
property_patterns = [
    # Crear obligación en propiedad
    path('properties/<int:property_id>/add_obligation/', 
         PropertyAddObligationView.as_view(), 
         name='property-add-obligation'),
    
    # Listar obligaciones de una propiedad
    path('properties/<int:property_id>/obligations/', 
         PropertyObligationsListView.as_view(), 
         name='property-obligations-list'),
    
    # Detalle de obligación específica
    path('properties/<int:property_id>/obligations/<int:obligation_id>/', 
         PropertyObligationDetailView.as_view(), 
         name='property-obligation-detail'),
    
    # Añadir pago a obligación
    path('properties/<int:property_id>/obligations/<int:obligation_id>/add_payment/', 
         ObligationAddPaymentView.as_view(), 
         name='obligation-add-payment'),
    
    # Listar pagos de obligación
    path('properties/<int:property_id>/obligations/<int:obligation_id>/payments/', 
         ObligationPaymentsListView.as_view(), 
         name='obligation-payments-list'),
    
    # Detalle de pago específico
    path('properties/<int:property_id>/obligations/<int:obligation_id>/payments/<int:payment_id>/', 
         ObligationPaymentDetailView.as_view(), 
         name='obligation-payment-detail'),
]

urlpatterns = [
    # Incluir rutas del router (obligation-types, payment-methods, obligations, notifications)
    path('', include(router.urls)),
    
    # Incluir rutas anidadas de properties
    path('', include(property_patterns)),
    
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]

