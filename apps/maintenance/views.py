from django.shortcuts import render
from rest_framework import viewsets

from apps.users.permissions import IsAdminUser
from .models import Repair
from .serializers import RepairSerializer

class RepairViewSet(viewsets.ModelViewSet):
    queryset = Repair.objects.all()
    serializer_class = RepairSerializer
    permission_classes = [IsAdminUser]  # Solo admins pueden gestionar reparaciones
