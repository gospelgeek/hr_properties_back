from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TenantViewSet, RentalViewSet,
    PropertyAddRentalView, PropertyRentalsListView, PropertyRentalDetailView,
    RentalAddPaymentView, RentalPaymentsListView, RentalPaymentDetailView,
    RentalsDashboardStatsView
)

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'rentals', RentalViewSet, basename='rental')

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard y estadísticas
    path('dashboard/stats/', RentalsDashboardStatsView.as_view(), name='rentals-dashboard-stats'),
    
    # Rutas para rentals de propiedades específicas
    path('properties/<int:property_id>/add_rental/', PropertyAddRentalView.as_view(), name='property-add-rental'),
    path('properties/<int:property_id>/rentals/', PropertyRentalsListView.as_view(), name='property-rentals-list'),
    path('properties/<int:property_id>/rentals/<int:rental_id>/', PropertyRentalDetailView.as_view(), name='property-rental-detail'),
    
    # Rutas para pagos de rentals específicos
    path('properties/<int:property_id>/rentals/<int:rental_id>/add_payment/', RentalAddPaymentView.as_view(), name='rental-add-payment'),
    path('properties/<int:property_id>/rentals/<int:rental_id>/payments/', RentalPaymentsListView.as_view(), name='rental-payments-list'),
    path('properties/<int:property_id>/rentals/<int:rental_id>/payments/<int:payment_id>/', RentalPaymentDetailView.as_view(), name='rental-payment-detail'),
]

'''
ENDPOINTS DISPONIBLES:

═══════════════════════════════════════════════════════════════════════
👥 TENANTS (Inquilinos)
═══════════════════════════════════════════════════════════════════════
GET    /api/tenants/                    - Listar todos los inquilinos
POST   /api/tenants/                    - Crear un inquilino
GET    /api/tenants/{id}/               - Ver detalle de un inquilino
PATCH  /api/tenants/{id}/               - Actualizar un inquilino
DELETE /api/tenants/{id}/               - Eliminar un inquilino

═══════════════════════════════════════════════════════════════════════
🏠 RENTALS (General) - CON FILTROS
═══════════════════════════════════════════════════════════════════════
GET    /api/rentals/                    - Listar todos los arriendos
GET    /api/rentals/{id}/               - Ver detalle completo de un arriendo
GET    /api/rentals/ending_soon/        - 🆕 Rentals que terminan pronto

FILTROS DISPONIBLES:
- ?status=occupied                       - Solo rentals ocupados
- ?status=available                      - Solo rentals disponibles
- ?rental_type=monthly                   - Solo rentals mensuales
- ?rental_type=airbnb                    - Solo rentals Airbnb
- ?ending_in_days=30                     - Rentals que terminan en X días

EJEMPLOS:
GET /api/rentals/?status=occupied&rental_type=monthly
GET /api/rentals/?ending_in_days=15
GET /api/rentals/ending_soon/?days=7&rental_type=monthly

═══════════════════════════════════════════════════════════════════════
📊 DASHBOARD - ESTADÍSTICAS DE RENTALS
═══════════════════════════════════════════════════════════════════════
GET /api/dashboard/stats/               - Estadísticas detalladas por tipo

RESPUESTA:
{
  "rentals": {
    "monthly_active": 5,
    "monthly_available": 2,
    "monthly_ending_soon": 1,
    "airbnb_active": 8,
    "airbnb_available": 3,
    "airbnb_ending_soon": 2
  }
}

═══════════════════════════════════════════════════════════════════════
🏘️ RENTALS DE PROPIEDADES ESPECÍFICAS
═══════════════════════════════════════════════════════════════════════
POST   /api/properties/{id}/add_rental/             - Crear rental para una propiedad
GET    /api/properties/{id}/rentals/                - Listar todos los rentals de la propiedad
GET    /api/properties/{id}/rentals/{rental_id}/    - Ver/editar/eliminar rental específico
PATCH  /api/properties/{id}/rentals/{rental_id}/    - Actualizar rental
DELETE /api/properties/{id}/rentals/{rental_id}/    - Eliminar rental

CREAR RENTAL (Ejemplo):
POST /api/properties/2/add_rental/
{
  "tenant": 1,
  "rental_type": "monthly",
  "check_in": "2026-02-01",
  "check_out": "2026-08-01",
  "amount": 1500000,
  "people_count": 2,
  "status": "occupied",
  "monthly_data": {
    "deposit_amount": 1500000,
    "is_refundable": true
  }
}

═══════════════════════════════════════════════════════════════════════
💳 PAGOS DE RENTALS
═══════════════════════════════════════════════════════════════════════
POST   /api/properties/{id}/rentals/{rental_id}/add_payment/                 - Añadir pago a un rental
GET    /api/properties/{id}/rentals/{rental_id}/payments/                    - Listar pagos de un rental
GET    /api/properties/{id}/rentals/{rental_id}/payments/{payment_id}/       - Ver/editar/eliminar pago específico
PATCH  /api/properties/{id}/rentals/{rental_id}/payments/{payment_id}/       - Actualizar pago
DELETE /api/properties/{id}/rentals/{rental_id}/payments/{payment_id}/       - Eliminar pago

CREAR PAGO (Ejemplo):
POST /api/properties/2/rentals/5/add_payment/
{
  "payment_method": 1,
  "payment_location": "oficina",
  "date": "2026-02-01",
  "amount": 1500000
}

NOTA: Para rentals Airbnb, el payment_method se asigna automáticamente como "Transferencia"

═══════════════════════════════════════════════════════════════════════
📋 FLUJO DE USO COMPLETO
═══════════════════════════════════════════════════════════════════════
1. Crear propiedad con use='rental'
2. Crear tenant (inquilino)
3. Crear rental en /api/properties/{id}/add_rental/ con datos de:
   - tenant (ID del inquilino)
   - rental_type ('monthly' o 'airbnb')
   - check_in, check_out, amount, people_count
   - status ('occupied' o 'available')
   - Si es 'monthly': monthly_data (deposit_amount, is_refundable, url_files)
   - Si es 'airbnb': airbnb_data (is_paid)
4. Añadir pagos en /api/properties/{id}/rentals/{rental_id}/add_payment/
5. Consultar estadísticas en /api/dashboard/stats/
6. Ver rentals que terminan pronto en /api/rentals/ending_soon/
'''
