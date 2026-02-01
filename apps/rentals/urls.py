from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TenantViewSet, RentalViewSet,
    PropertyAddRentalView, PropertyRentalsListView, PropertyRentalDetailView,
    RentalAddPaymentView, RentalPaymentsListView, RentalPaymentDetailView
)

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'rentals', RentalViewSet, basename='rental')

urlpatterns = [
    path('', include(router.urls)),
    
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

--- TENANTS ---
GET    /api/tenants/                    - Listar todos los inquilinos
POST   /api/tenants/                    - Crear un inquilino
GET    /api/tenants/{id}/               - Ver detalle de un inquilino
PATCH  /api/tenants/{id}/               - Actualizar un inquilino
DELETE /api/tenants/{id}/               - Eliminar un inquilino

--- RENTALS (General) ---
GET    /api/rentals/                    - Listar todos los arriendos
GET    /api/rentals/{id}/               - Ver detalle completo de un arriendo

--- RENTALS DE PROPIEDADES ESPECÍFICAS ---
POST   /api/properties/{id}/add_rental/             - Crear rental para una propiedad (valida que sea de arrendamiento)
GET    /api/properties/{id}/rentals/                - Listar todos los rentals de la propiedad
GET    /api/properties/{id}/rentals/{rental_id}/    - Ver/editar/eliminar rental específico
PATCH  /api/properties/{id}/rentals/{rental_id}/    - Actualizar rental
DELETE /api/properties/{id}/rentals/{rental_id}/    - Eliminar rental

--- PAGOS DE RENTALS ---
POST   /api/properties/{id}/rentals/{rental_id}/add_payment/                 - Añadir pago a un rental
GET    /api/properties/{id}/rentals/{rental_id}/payments/                    - Listar pagos de un rental
GET    /api/properties/{id}/rentals/{rental_id}/payments/{payment_id}/       - Ver/editar/eliminar pago específico
PATCH  /api/properties/{id}/rentals/{rental_id}/payments/{payment_id}/       - Actualizar pago
DELETE /api/properties/{id}/rentals/{rental_id}/payments/{payment_id}/       - Eliminar pago

--- FLUJO DE USO ---
1. Crear propiedad con use='arrendamiento'
2. Crear tenant
3. Crear rental en /api/properties/{id}/add_rental/ con datos de:
   - tenant (ID del inquilino)
   - rental_type ('monthly' o 'airbnb')
   - check_in, check_out, amount, people_count
   - Si es 'monthly': monthly_data (deposit_amount, is_refundable, url_files)
   - Si es 'airbnb': airbnb_data (is_paid)
4. Añadir pagos en /api/properties/{id}/rentals/{rental_id}/add_payment/
'''
