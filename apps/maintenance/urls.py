from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairViewSet

router = DefaultRouter()
router.register(r'repairs', RepairViewSet, basename='repair')

urlpatterns = [
    path('', include(router.urls)),
]