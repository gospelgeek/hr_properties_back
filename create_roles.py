"""
Script simple para crear roles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_properties.settings')
django.setup()

from apps.users.models import Role

# Crear roles
roles_created = []
for role_name in ['admin', 'cliente', 'invitado']:
    role, created = Role.objects.get_or_create(name=role_name)
    if created:
        roles_created.append(role_name)
        print(f"✅ Rol '{role_name}' creado")
    else:
        print(f"ℹ️  Rol '{role_name}' ya existe")

if roles_created:
    print(f"\n✅ {len(roles_created)} rol(es) nuevo(s) creado(s)")
else:
    print("\nℹ️  Todos los roles ya existían")

print("\n✅ Sistema listo para usar")
