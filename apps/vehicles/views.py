from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser
from .models import (
	Vehicle,
	VehicleDocument,
	VehicleImages,
	VehicleRepair,
	Responsible,
	ObligationVehicle,
	ObligationVehicleType,
	VehiclePayment,
)
from .seralizers import (
	VehicleSerializer,
	VehicleDocumentSerializer,
	VehicleImageSerializer,
	VehicleRepairSerializer,
	ResponsibleSerializer,
	VehicleDocumentCreateSerializer,
	VehicleImageCreateSerializer,
	VehicleRepairCreateSerializer,
	ResponsibleCreateSerializer,
	ObligationVehicleSerializer,
	ObligationVehicleCreateSerializer,
	ObligationVehicleTypeSerializer,
	VehiclePaymentSerializer,
	VehiclePaymentCreateSerializer,
)


class VehicleViewSet(viewsets.ModelViewSet):
	queryset = Vehicle.objects.all().prefetch_related(
		'documents',
		'images',
		'responsible',
		'repairs',
		'obligations_vehicle',
		'obligations_vehicle__payments',
	)
	serializer_class = VehicleSerializer
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	@action(detail=True, methods=['get'])
	def documents(self, request, pk=None):
		vehicle = self.get_object()
		serializer = VehicleDocumentSerializer(vehicle.documents.all(), many=True, context={'request': request})
		return Response(serializer.data)

	@action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
	def add_document(self, request, pk=None):
		vehicle = self.get_object()
		serializer = VehicleDocumentCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		document = serializer.save(vehicle=vehicle)
		return Response(
			VehicleDocumentSerializer(document, context={'request': request}).data,
			status=status.HTTP_201_CREATED,
		)
	@action(detail=True, methods=['delete'])
	def delete_document(self, request, pk=None, doc_id=None):
		vehicle = self.get_object()
		doc_id = doc_id or request.query_params.get('doc_id') or request.data.get('doc_id')
		if not doc_id:
			return Response({'detail': 'doc_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
		document = get_object_or_404(VehicleDocument, pk=doc_id, vehicle=vehicle)
		document.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['get'])
	def images(self, request, pk=None):
		vehicle = self.get_object()
		serializer = VehicleImageSerializer(vehicle.images.all(), many=True, context={'request': request})
		return Response(serializer.data)

	@action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
	def add_image(self, request, pk=None):
		vehicle = self.get_object()
		serializer = VehicleImageCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		image = serializer.save(vehicle=vehicle)
		return Response(
			VehicleImageSerializer(image, context={'request': request}).data,
			status=status.HTTP_201_CREATED,
		)
	@action(detail=True, methods=['delete'])
	def delete_image(self, request, pk=None, img_id=None):
		vehicle = self.get_object()
		img_id = img_id or request.query_params.get('img_id') or request.data.get('img_id')
		if not img_id:
			return Response({'detail': 'img_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
		image = get_object_or_404(VehicleImages, pk=img_id, vehicle=vehicle)
		image.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['get'])
	def responsibles(self, request, pk=None):
		vehicle = self.get_object()
		serializer = ResponsibleSerializer(vehicle.responsible.all(), many=True, context={'request': request})
		return Response(serializer.data)

	@action(detail=True, methods=['post'])
	def add_responsible(self, request, pk=None):
		vehicle = self.get_object()
		responsible_id = request.data.get('responsible_id')
		if responsible_id:
			responsible = get_object_or_404(Responsible, pk=responsible_id)
		else:
			serializer = ResponsibleCreateSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			responsible = serializer.save()

		vehicle.responsible.add(responsible)
		return Response(
			ResponsibleSerializer(responsible, context={'request': request}).data,
			status=status.HTTP_201_CREATED,
		)

	@action(detail=True, methods=['post'])
	def remove_responsible(self, request, pk=None):
		vehicle = self.get_object()
		responsible_id = request.data.get('responsible_id')
		if not responsible_id:
			return Response({'detail': 'responsible_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

		responsible = get_object_or_404(Responsible, pk=responsible_id)
		vehicle.responsible.remove(responsible)
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['get'])
	def obligations(self, request, pk=None):
		vehicle = self.get_object()
		serializer = ObligationVehicleSerializer(vehicle.obligations_vehicle.all(), many=True, context={'request': request})
		return Response(serializer.data)

	@action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
	def add_obligation(self, request, pk=None):
		vehicle = self.get_object()
		serializer = ObligationVehicleCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		obligation = serializer.save(vehicle=vehicle)
		return Response(
			ObligationVehicleSerializer(obligation, context={'request': request}).data,
			status=status.HTTP_201_CREATED,
		)

	@action(detail=True, methods=['get'])
	def obligation_payments(self, request, pk=None):
		vehicle = self.get_object()
		obligation_id = request.query_params.get('obligation_id')
		if not obligation_id:
			return Response({'detail': 'obligation_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

		obligation = get_object_or_404(ObligationVehicle, pk=obligation_id, vehicle=vehicle)
		serializer = VehiclePaymentSerializer(obligation.payments.all(), many=True, context={'request': request})
		return Response(serializer.data)

	@action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
	def add_obligation_payment(self, request, pk=None):
		vehicle = self.get_object()
		obligation_id = request.data.get('obligation_id')
		if not obligation_id:
			return Response({'detail': 'obligation_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

		obligation = get_object_or_404(ObligationVehicle, pk=obligation_id, vehicle=vehicle)
		serializer = VehiclePaymentCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		total_paid = sum(payment.amount for payment in obligation.payments.all())
		new_amount = serializer.validated_data['amount']
		if total_paid + new_amount > obligation.amount:
			return Response(
				{
					'error': 'Payment exceeds the obligation amount',
					'obligation_amount': obligation.amount,
					'already_paid': total_paid,
					'pending': obligation.amount - total_paid,
					'attempted': new_amount,
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

		payment = serializer.save(obligation=obligation)
		new_total_paid = total_paid + new_amount
		return Response(
			{
				'message': 'Payment registered successfully',
				'payment': VehiclePaymentSerializer(payment, context={'request': request}).data,
				'obligation_status': {
					'total_amount': obligation.amount,
					'total_paid': new_total_paid,
					'pending': obligation.amount - new_total_paid,
					'is_fully_paid': new_total_paid >= obligation.amount,
				},
			},
			status=status.HTTP_201_CREATED,
		)

	@action(detail=True, methods=['get'])
	def repairs(self, request, pk=None):
		vehicle = self.get_object()
		serializer = VehicleRepairSerializer(vehicle.repairs.all(), many=True, context={'request': request})
		return Response(serializer.data)

	@action(detail=True, methods=['post'])
	def add_repair(self, request, pk=None):
		vehicle = self.get_object()
		serializer = VehicleRepairCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		repair = serializer.save(vehicle=vehicle)
		return Response(
			VehicleRepairSerializer(repair, context={'request': request}).data,
			status=status.HTTP_201_CREATED,
		)


class VehicleDocumentViewSet(viewsets.ModelViewSet):
	queryset = VehicleDocument.objects.select_related('vehicle').all()
	serializer_class = VehicleDocumentSerializer
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]


class VehicleImageViewSet(viewsets.ModelViewSet):
	queryset = VehicleImages.objects.select_related('vehicle').all()
	serializer_class = VehicleImageSerializer
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]


class ResponsibleViewSet(viewsets.ModelViewSet):
	queryset = Responsible.objects.prefetch_related('vehicles').all()
	serializer_class = ResponsibleSerializer
	permission_classes = [IsAdminUser]


class VehicleRepairViewSet(viewsets.ModelViewSet):
	queryset = VehicleRepair.objects.select_related('vehicle').all()
	serializer_class = VehicleRepairSerializer
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]


class ObligationVehicleTypeViewSet(viewsets.ModelViewSet):
	queryset = ObligationVehicleType.objects.all()
	serializer_class = ObligationVehicleTypeSerializer
	permission_classes = [IsAdminUser]


class ObligationVehicleViewSet(viewsets.ModelViewSet):
	queryset = ObligationVehicle.objects.select_related('vehicle', 'obligation_type').prefetch_related('payments').all()
	serializer_class = ObligationVehicleSerializer
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]


class VehiclePaymentViewSet(viewsets.ModelViewSet):
	queryset = VehiclePayment.objects.select_related('obligation', 'payment_method').all()
	serializer_class = VehiclePaymentSerializer
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]


class VehicleObligationPaymentsViewSet(viewsets.ViewSet):
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def list(self, request, vehicle_pk=None, obligation_pk=None):
		obligation = get_object_or_404(ObligationVehicle, pk=obligation_pk, vehicle_id=vehicle_pk)
		serializer = VehiclePaymentSerializer(obligation.payments.all(), many=True, context={'request': request})
		return Response(serializer.data)

	def create(self, request, vehicle_pk=None, obligation_pk=None):
		obligation = get_object_or_404(ObligationVehicle, pk=obligation_pk, vehicle_id=vehicle_pk)
		serializer = VehiclePaymentCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		total_paid = sum(payment.amount for payment in obligation.payments.all())
		new_amount = serializer.validated_data['amount']
		if total_paid + new_amount > obligation.amount:
			return Response(
				{
					'error': 'Payment exceeds the obligation amount',
					'obligation_amount': obligation.amount,
					'already_paid': total_paid,
					'pending': obligation.amount - total_paid,
					'attempted': new_amount,
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

		payment = serializer.save(obligation=obligation)
		new_total_paid = total_paid + new_amount
		return Response(
			{
				'message': 'Payment registered successfully',
				'payment': VehiclePaymentSerializer(payment, context={'request': request}).data,
				'obligation_status': {
					'total_amount': obligation.amount,
					'total_paid': new_total_paid,
					'pending': obligation.amount - new_total_paid,
					'is_fully_paid': new_total_paid >= obligation.amount,
				},
			},
			status=status.HTTP_201_CREATED,
		)
