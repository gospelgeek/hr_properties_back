"""
Señales para la app de rentals

Auto-creación de usuarios cuando se crea un Tenant
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Tenant
from apps.users.models import Role, UserRole

User = get_user_model()


@receiver(post_save, sender=Tenant)
def create_client_user_for_tenant(sender, instance, created, **kwargs):
    """
    Crea automáticamente un User con rol 'cliente' cuando se crea un Tenant
    
    Credenciales generadas:
    - Email: email del tenant
    - Username: phone1 (único)
    - Password: phone1 + birth_year (ej: "31234567891990")
    """
    if created:
        # Generar password: phone1 + birth_year
        password = f"{instance.phone1}{instance.birth_year}"
        
        # Crear el usuario
        user = User.objects.create_user(
            username=instance.phone1,  # Username es el teléfono
            email=instance.email,
            password=password,
            name=f"{instance.name} {instance.lastname}"
        )
        
        # Asignar rol 'cliente'
        cliente_role, _ = Role.objects.get_or_create(name=Role.CLIENTE)
        UserRole.objects.create(user=user, role=cliente_role)
        
        print(f"✅ User creado para tenant {instance.full_name}")
        print(f"   Username: {instance.phone1}")
        print(f"   Password: {password}")
