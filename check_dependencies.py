"""
Script para verificar e instalar dependencias necesarias
"""
import subprocess
import sys

def check_package(package_name):
    """Verificar si un paquete está instalado"""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    
    packages = [
        ('django', 'Django'),
        ('rest_framework', 'djangorestframework'),
        ('rest_framework_simplejwt', 'djangorestframework-simplejwt'),
        ('google.auth', 'google-auth'),
        ('django_filters', 'django-filter'),
    ]
    
    missing = []
    
    for module_name, package_name in packages:
        if check_package(module_name):
            print(f"  ✅ {package_name}")
        else:
            print(f"  ❌ {package_name} - FALTA")
            missing.append(package_name)
    
    if missing:
        print("\n" + "=" * 60)
        print("⚠️  DEPENDENCIAS FALTANTES")
        print("=" * 60)
        print("\nPara instalar las dependencias faltantes, ejecuta:")
        print(f"\npip install {' '.join(missing)}")
        print("\nO instala todas desde requirements.txt:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✅ Todas las dependencias están instaladas")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
