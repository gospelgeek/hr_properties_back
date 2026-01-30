from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, PropertyDetailsViewSet, PropertyMediaViewSet,
    PropertyLawViewSet, EnserViewSet, EnserInventoryViewSet
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
]