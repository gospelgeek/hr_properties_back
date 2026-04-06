from django.contrib import admin

# Register your models here.
from .models import Vehicle, VehicleRepair, Responsible, VehicleImages, VehicleDocument, ObligationVehicleType, ObligationVehicle, VehiclePayment

admin.site.register(Vehicle)
admin.site.register(Responsible)
admin.site.register(VehicleImages)
admin.site.register(VehicleDocument)
admin.site.register(ObligationVehicleType)
admin.site.register(ObligationVehicle)
admin.site.register(VehiclePayment)
admin.site.register(VehicleRepair)