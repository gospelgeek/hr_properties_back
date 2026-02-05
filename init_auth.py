"""
Script de inicialización del sistema de autenticación
Ejecutar con: python init_auth.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_properties.settings')
django.setup()

from apps.users.models import Role

def create_roles():
    """Crear roles iniciales del sistema"""
    print("🔧 Creando roles del sistema...")
    
    roles = ['admin', 'cliente', 'invitado']
    created = []
    
    for role_name in roles:
        role, created_now = Role.objects.get_or_create(name=role_name)
        if created_now:
            created.append(role_name)
            print(f"  ✅ Rol '{role_name}' creado")
        else:
            print(f"  ℹ️  Rol '{role_name}' ya existe")
    
    if created:
        print(f"\n✅ {len(created)} rol(es) nuevo(s) creado(s)")
    else:
        print("\nℹ️  Todos los roles ya existían")
    
    return True


def verify_settings():
    """Verificar configuraciones necesarias"""
    print("\n🔍 Verificando configuraciones...")
    
    from django.conf import settings
    
    issues = []
    
    # Verificar GOOGLE_OAUTH_CLIENT_ID
    if not hasattr(settings, 'GOOGLE_OAUTH_CLIENT_ID') or not settings.GOOGLE_OAUTH_CLIENT_ID:
        issues.append("⚠️  GOOGLE_OAUTH_CLIENT_ID no está configurado en settings.py")
    else:
        print("  ✅ GOOGLE_OAUTH_CLIENT_ID configurado")
    
    # Verificar ADMIN_EMAILS en .env
    admin_emails = os.getenv('ADMIN_EMAILS')
    if not admin_emails:
        issues.append("⚠️  ADMIN_EMAILS no está configurado en .env")
    else:
        print(f"  ✅ ADMIN_EMAILS configurado: {admin_emails}")
    
    # Verificar Simple JWT en INSTALLED_APPS
    if 'rest_framework_simplejwt' not in settings.INSTALLED_APPS:
        issues.append("⚠️  rest_framework_simplejwt no está en INSTALLED_APPS")
    else:
        print("  ✅ rest_framework_simplejwt instalado")
    
    # Verificar blacklist
    if 'rest_framework_simplejwt.token_blacklist' not in settings.INSTALLED_APPS:
        issues.append("⚠️  rest_framework_simplejwt.token_blacklist no está en INSTALLED_APPS")
    else:
        print("  ✅ token_blacklist instalado")
    
    # Verificar REST_FRAMEWORK settings
    if not hasattr(settings, 'REST_FRAMEWORK'):
        issues.append("⚠️  REST_FRAMEWORK no está configurado en settings.py")
    else:
        print("  ✅ REST_FRAMEWORK configurado")
    
    # Verificar SIMPLE_JWT settings
    if not hasattr(settings, 'SIMPLE_JWT'):
        issues.append("⚠️  SIMPLE_JWT no está configurado en settings.py")
    else:
        print("  ✅ SIMPLE_JWT configurado")
    
    if issues:
        print("\n❌ Se encontraron problemas de configuración:")
        for issue in issues:
            print(f"  {issue}")
        print("\nConsultar AUTHENTICATION_SETUP.md para más detalles")
        return False
    else:
        print("\n✅ Todas las configuraciones están correctas")
        return True


def create_test_tenant():
    """Crear un tenant de prueba para testing"""
    print("\n📱 ¿Deseas crear un tenant de prueba? (s/n): ", end='')
    response = input().strip().lower()
    
    if response != 's':
        print("  ⏭️  Omitiendo creación de tenant de prueba")
        return
    
    from apps.rentals.models import Tenant
    
    print("\nIngresa los datos del tenant de prueba:")
    name = input("  Nombre: ").strip() or "Juan"
    lastname = input("  Apellido: ").strip() or "Pérez"
    email = input("  Email: ").strip() or "juan@test.com"
    phone1 = input("  Teléfono (username): ").strip() or "3123456789"
    birth_year = input("  Año de nacimiento: ").strip() or "1990"
    
    try:
        birth_year = int(birth_year)
    except ValueError:
        print("  ❌ Año de nacimiento inválido")
        return
    
    try:
        tenant = Tenant.objects.create(
            name=name,
            lastname=lastname,
            email=email,
            phone1=phone1,
            birth_year=birth_year
        )
        
        print(f"\n✅ Tenant creado exitosamente:")
        print(f"  👤 Nombre: {tenant.full_name}")
        print(f"  📧 Email: {tenant.email}")
        print(f"  📱 Username: {tenant.phone1}")
        print(f"  🔑 Password: {tenant.phone1}{tenant.birth_year}")
        print(f"\n  Prueba el login en: POST /api/users/login/")
        
    except Exception as e:
        print(f"  ❌ Error al crear tenant: {e}")


def show_summary():
    """Mostrar resumen de la configuración"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE CONFIGURACIÓN")
    print("="*60)
    
    from apps.users.models import Role
    
    roles = Role.objects.all()
    print(f"\n👥 Roles disponibles: {roles.count()}")
    for role in roles:
        print(f"  - {role.name}")
    
    from apps.rentals.models import Tenant
    tenants = Tenant.objects.all()
    print(f"\n📱 Tenants registrados: {tenants.count()}")
    
    from apps.users.models import User
    users = User.objects.all()
    print(f"👤 Usuarios registrados: {users.count()}")
    
    print("\n📚 Documentación:")
    print("  - AUTHENTICATION_SETUP.md (configuración completa)")
    print("  - AUTHENTICATION_IMPLEMENTATION_SUMMARY.md (resumen)")
    print("  - apps/users/urls.py (endpoints disponibles)")
    print("  - apps/users/permissions.py (permisos y ejemplos)")
    
    print("\n🚀 Próximos pasos:")
    print("  1. Verificar que settings.py tenga las configuraciones")
    print("  2. Configurar .env con GOOGLE_OAUTH_CLIENT_ID y ADMIN_EMAILS")
    print("  3. Ejecutar migraciones: python manage.py migrate")
    print("  4. Aplicar permisos a los ViewSets")
    print("  5. Probar endpoints de autenticación")
    
    print("\n" + "="*60)


def main():
    """Función principal"""
    print("="*60)
    print("🔐 INICIALIZACIÓN DE SISTEMA DE AUTENTICACIÓN")
    print("="*60)
    
    try:
        # 1. Crear roles
        create_roles()
        
        # 2. Verificar configuraciones
        verify_settings()
        
        # 3. Crear tenant de prueba (opcional)
        create_test_tenant()
        
        # 4. Mostrar resumen
        show_summary()
        
        print("\n✅ Inicialización completada")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
