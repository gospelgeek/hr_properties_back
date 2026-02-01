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

2. PAYMENT METHODS (Métodos de pago):
   - GET    /api/payment-methods/           → Listar todos
   - POST   /api/payment-methods/           → Crear nuevo
   - GET    /api/payment-methods/{id}/      → Ver detalle
   - PUT    /api/payment-methods/{id}/      → Actualizar completo
   - PATCH  /api/payment-methods/{id}/      → Actualizar parcial
   - DELETE /api/payment-methods/{id}/      → Eliminar

3. OBLIGATIONS (Todas las obligaciones del sistema):
   - GET    /api/obligations/               → Listar todas con pagos
   - GET    /api/obligations/{id}/          → Ver detalle con pagos
   - PUT    /api/obligations/{id}/          → Actualizar completo
   - PATCH  /api/obligations/{id}/          → Actualizar parcial
   - DELETE /api/obligations/{id}/          → Eliminar

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

# 2. Crear datos iniciales
POST /api/payment-methods/
{
  "name": "Transferencia"
}

POST /api/obligation-types/
{
  "name": "tax"
}

# 3. Probar flujo completo en una propiedad
POST /api/properties/2/add_obligation/
POST /api/properties/2/obligations/1/add_payment/

═══════════════════════════════════════════════════════════════════════
📊 FLUJO DE TRABAJO TÍPICO
═══════════════════════════════════════════════════════════════════════

1. Crear tipos de obligaciones (impuestos, servicios, etc.)
2. Crear métodos de pago (efectivo, transferencia, etc.)
3. Crear propiedad
4. Añadir obligaciones a la propiedad
5. Registrar pagos de obligaciones
6. Consultar estado de pagos y montos pendientes

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
)

# Router para ViewSets (CRUD completo)
router = DefaultRouter()
router.register(r'obligation-types', ObligationTypeViewSet, basename='obligation-type')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'obligations', ObligationViewSet, basename='obligation')

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
    # Incluir rutas del router
    path('', include(router.urls)),
    
    # Incluir rutas anidadas de properties
    path('', include(property_patterns)),
]
