from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, PropertyDetailsViewSet, PropertyMediaViewSet,
    PropertyLawViewSet, EnserViewSet, EnserInventoryViewSet, 
    PropertyAddRepairView, PropertyUploadMediaView, PropertyAddEnserView,
  PropertyAddLawView, PropertyLawDetailView, PropertyMediaDetailView
)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'property-details', PropertyDetailsViewSet, basename='property-details')
router.register(r'property-media', PropertyMediaViewSet, basename='property-media')
router.register(r'property-laws', PropertyLawViewSet, basename='property-law')
router.register(r'enseres', EnserViewSet, basename='enser')
router.register(r'enser-inventory', EnserInventoryViewSet, basename='enser-inventory')

urlpatterns = [
    path('', include(router.urls)),
    path('properties/<int:property_id>/add_repair/', PropertyAddRepairView.as_view(), name='property-add-repair'),
    path('properties/<int:property_id>/upload_media/', PropertyUploadMediaView.as_view(), name='property-upload-media'),
    path('properties/<int:property_id>/add_enser/', PropertyAddEnserView.as_view(), name='property-add-enser'),
    path('properties/<int:property_id>/add_law/', PropertyAddLawView.as_view(), name='property-add-law'),
    path('properties/<int:property_id>/laws/<int:law_id>/', PropertyLawDetailView.as_view(), name='property-law-detail'),
    path('properties/<int:property_id>/media/<int:media_id>/', PropertyMediaDetailView.as_view(), name='property-media-detail'),
]

'''
═══════════════════════════════════════════════════════════════════════
🏠 PROPERTIES - ENDPOINTS DISPONIBLES
═══════════════════════════════════════════════════════════════════════

--- CRUD BÁSICO ---
POST   /api/properties/                 - Crear propiedad
GET    /api/properties/                 - Listar (solo activas, no soft-deleted)
GET    /api/properties/{id}/            - Obtener por ID (detalle completo con enseres)
PUT    /api/properties/{id}/            - Actualizar completo
PATCH  /api/properties/{id}/            - Actualizar parcial
DELETE /api/properties/{id}/            - Soft delete (no borra físicamente)

--- FILTROS AVANZADOS ---
GET /api/properties/?use=rental                              - Por tipo de uso
GET /api/properties/?rental_status=active                    - Con rental activo
GET /api/properties/?rental_status=available                 - Propiedades disponibles
GET /api/properties/?rental_status=ending_soon               - 🆕 Rentals terminan en 30 días
GET /api/properties/?rental_type=monthly                     - Con rentals mensuales
GET /api/properties/?rental_type=airbnb                      - Con rentals Airbnb

EJEMPLOS COMBINADOS:
GET /api/properties/?use=rental&rental_status=active&rental_type=monthly
GET /api/properties/?rental_status=ending_soon&rental_type=airbnb
GET /api/properties/?rental_status=active,available          - Múltiples estados

💡 EJEMPLOS DE CONSULTAS REALES:
# 1. Ver todas las propiedades de rental
GET /api/properties/?use=rental

# 2. Ver propiedades comerciales
GET /api/properties/?use=commercial

# 3. Ver propiedades de rental con rental activo (ocupadas)
GET /api/properties/?use=rental&rental_status=active

# 4. Ver propiedades de rental disponibles para arrendar
GET /api/properties/?rental_status=available

# 5. Ver propiedades con rentals mensuales activos
GET /api/properties/?rental_type=monthly&rental_status=active

# 6. Ver propiedades con rentals Airbnb disponibles
GET /api/properties/?rental_type=airbnb&rental_status=available

# 7. Ver propiedades con rentals que terminan en 30 días (ending_soon)
GET /api/properties/?rental_status=ending_soon

# 8. Ver propiedades con rentals mensuales que terminan pronto
GET /api/properties/?rental_status=ending_soon&rental_type=monthly

# 9. Ver propiedades con rentals Airbnb que terminan pronto
GET /api/properties/?rental_status=ending_soon&rental_type=airbnb

# 10. Combinar: propiedades de rental que están activas O disponibles
GET /api/properties/?use=rental&rental_status=active,available

# 11. Ver propiedades personales (no de rental)
GET /api/properties/?use=personal

# 12. Ver solo propiedades con rentals mensuales (sin importar estado)
GET /api/properties/?rental_type=monthly

# 13. Ver propiedades con múltiples tipos de rental
GET /api/properties/?rental_type=monthly,airbnb

NOTA: Los filtros rental_status y rental_type aceptan múltiples valores separados por coma

--- ACCIONES ESPECIALES ---
POST /api/properties/{id}/soft_delete/  - Soft delete manual
POST /api/properties/{id}/restore/      - Restaurar propiedad eliminada
GET  /api/properties/deleted/           - Ver propiedades eliminadas
GET  /api/properties/choices/           - Obtener opciones de campos (use, type_building)

--- FINANZAS Y ESTADÍSTICAS ---
GET /api/properties/{id}/repairs_cost/  - Total de reparaciones
GET /api/properties/{id}/financials/    - Resumen financiero completo
   Respuesta: {
     "income": { "rental_payments": 5000000, "total_income": 5000000 },
     "expenses": { "obligations": 1200000, "repairs": 800000, "total_expenses": 2000000 },
     "balance": 3000000
   }

--- GESTIÓN DE LEYES/REGULACIONES ---
GET    /api/properties/{id}/laws/               - Listar todas las PropertyLaws
POST   /api/properties/{id}/add_law/            - Añadir ley/regulación
GET    /api/properties/{id}/laws/{law_id}/      - Ver detalle de ley
PUT    /api/properties/{id}/laws/{law_id}/      - Actualizar ley
PATCH  /api/properties/{id}/laws/{law_id}/      - Actualizar parcial
DELETE /api/properties/{id}/laws/{law_id}/      - Eliminar ley

--- GESTIÓN DE MEDIA ---
POST /api/properties/{id}/upload_media/         - Subir archivos multimedia
   Body (FormData): {
     "files": [archivo1, archivo2],
     "media_type": "image"  // o "video", "document"
   }

--- REPARACIONES ---
POST /api/properties/{id}/add_repair/           - Añadir reparación
   Body: {
     "description": "Reparar tubería",
     "cost": 500000,
     "date": "2026-02-01"
   }

--- ENSERES/INVENTARIO ---
POST /api/properties/{id}/add_enser/            - Crear enser y añadir al inventario
   Body: {
     "name": "Nevera",
     "price": 1200000,
     "condition": "good",
     "url_media": <archivo opcional>
   }

═══════════════════════════════════════════════════════════════════════
📊 OTROS VIEWSETS
═══════════════════════════════════════════════════════════════════════

PROPERTY DETAILS:
GET    /api/property-details/           - Listar todos
POST   /api/property-details/           - Crear
GET    /api/property-details/{id}/      - Ver detalle
PATCH  /api/property-details/{id}/      - Actualizar

PROPERTY MEDIA:
GET    /api/property-media/             - Listar todos los archivos
POST   /api/property-media/             - Crear registro de media
GET    /api/property-media/choices/     - Opciones de media_type

ENSERES:
GET    /api/enseres/                    - Listar todos
POST   /api/enseres/                    - Crear enser
GET    /api/enseres/choices/            - Opciones de condition

ENSER INVENTORY:
GET    /api/enser-inventory/            - Listar todo el inventario
'''