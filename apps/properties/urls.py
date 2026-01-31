from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, PropertyDetailsViewSet, PropertyMediaViewSet,
    PropertyLawViewSet, EnserViewSet, EnserInventoryViewSet, 
    PropertyAddRepairView, PropertyUploadMediaView, PropertyAddEnserView
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
]

'''
POST /api/properties/ - Crear propiedad
GET /api/properties/ - Listar (solo activas)
GET /api/properties/{id}/ - Obtener por ID (con enseres incluidos)
PUT/PATCH /api/properties/{id}/ - Actualizar
DELETE /api/properties/{id}/ - Soft delete (no borra físicamente)
POST /api/properties/{id}/restore/ - Restaurar eliminada
GET /api/properties/deleted/ - Ver propiedades eliminadas
POST /api/properties/{id}/upload_media/ - Subir archivos (solo files y media_type)
POST /api/properties/{id}/add_repair/ - Añadir reparación a la propiedad
POST /api/properties/{id}/add_enser/ - Añadir enser al inventario de la propiedad
'''