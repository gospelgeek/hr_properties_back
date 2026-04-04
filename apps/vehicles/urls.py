from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
	VehicleViewSet,
	VehicleDocumentViewSet,
	VehicleImageViewSet,
	ResponsibleViewSet,
	VehicleRepairViewSet,
	ObligationVehicleTypeViewSet,
	ObligationVehicleViewSet,
	VehiclePaymentViewSet,
	VehicleObligationPaymentsViewSet,
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'vehicle-documents', VehicleDocumentViewSet, basename='vehicle-document')
router.register(r'vehicle-images', VehicleImageViewSet, basename='vehicle-image')
router.register(r'vehicle-responsibles', ResponsibleViewSet, basename='vehicle-responsible')
router.register(r'vehicle-repairs', VehicleRepairViewSet, basename='vehicle-repair')
router.register(r'vehicle-obligation-types', ObligationVehicleTypeViewSet, basename='vehicle-obligation-type')
router.register(r'vehicle-obligations', ObligationVehicleViewSet, basename='vehicle-obligation')
router.register(r'vehicle-payments', VehiclePaymentViewSet, basename='vehicle-payment')

urlpatterns = [
	path(
		'vehicles/<int:vehicle_pk>/obligations/<int:obligation_pk>/payments/',
		VehicleObligationPaymentsViewSet.as_view({'get': 'list', 'post': 'create'}),
		name='vehicle-obligation-payments',
	),
	path('', include(router.urls)),
]
