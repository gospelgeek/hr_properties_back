from rest_framework import serializers
from .models import Repair

class RepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repair
        fields = [
            'id',
            'property',
            'cost',
            'date',
            'observation',
            'description'
        ]
        read_only_fields = ['id']