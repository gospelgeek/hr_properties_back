from django.contrib import admin
from .models import Property, PropertyLaw, Enser, EnserInventory, PropertyDetails, PropertyMedia

# Register your models here.
admin.site.register(Property)
admin.site.register(PropertyLaw)
admin.site.register(Enser)
admin.site.register(EnserInventory)
admin.site.register(PropertyDetails)
admin.site.register(PropertyMedia)


