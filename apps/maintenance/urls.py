from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairViewSet

router = DefaultRouter()
router.register(r'repairs', RepairViewSet, basename='repair')

urlpatterns = [
    path('', include(router.urls)),
]

'''
POST /api/repairs/ - Crear reparación
GET /api/repairs/ - Listar todas las reparaciones (incluye información de la propiedad)
GET /api/repairs/{id}/ - Obtener reparación por ID
PUT/PATCH /api/repairs/{id}/ - Actualizar reparación
DELETE /api/repairs/{id}/ - Eliminar reparación
GET /api/repairs/?property={property_id} - Filtrar reparaciones por propiedad

También puedes crear reparaciones desde la propiedad:
POST /api/properties/{id}/add_repair/ - Añadir reparación a una propiedad específica
'''