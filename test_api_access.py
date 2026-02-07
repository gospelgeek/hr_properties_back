"""
Script para probar el acceso público y privado a la API de propiedades

Ejecutar con: python test_api_access.py
"""

import requests

BASE_URL = "http://localhost:8000"

def test_public_access():
    """Probar acceso público a propiedades disponibles"""
    print("\n" + "="*80)
    print("🔓 TEST: Acceso PÚBLICO a propiedades disponibles")
    print("="*80)
    
    # 1. Listar propiedades disponibles (sin autenticación)
    print("\n1️⃣  GET /api/properties/?rental_status=available (SIN TOKEN)")
    response = requests.get(f"{BASE_URL}/api/properties/?rental_status=available")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Éxito: {len(response.json())} propiedades encontradas")
        if response.json():
            print(f"   Primera propiedad: {response.json()[0].get('name')}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 2. Intentar listar propiedades ocupadas (debe fallar)
    print("\n2️⃣  GET /api/properties/?rental_status=occupied (SIN TOKEN)")
    response = requests.get(f"{BASE_URL}/api/properties/?rental_status=occupied")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ✅ Correcto: Acceso denegado (401 Unauthorized)")
    else:
        print(f"   ❌ Error: Debería retornar 401, retornó {response.status_code}")
    
    # 3. Intentar crear propiedad (debe fallar)
    print("\n3️⃣  POST /api/properties/ (SIN TOKEN)")
    response = requests.post(f"{BASE_URL}/api/properties/", json={"name": "Test"})
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ✅ Correcto: Acceso denegado (401 Unauthorized)")
    else:
        print(f"   ❌ Error: Debería retornar 401, retornó {response.status_code}")


def test_admin_access():
    """Probar acceso de administrador a todas las propiedades"""
    print("\n" + "="*80)
    print("🔒 TEST: Acceso ADMIN a todas las propiedades")
    print("="*80)
    print("\n⚠️  Para probar este test necesitas:")
    print("   1. Crear un usuario admin")
    print("   2. Obtener un token de autenticación")
    print("   3. Reemplazar 'YOUR_ADMIN_TOKEN_HERE' en este script")
    
    # Reemplaza esto con tu token real
    TOKEN = "YOUR_ADMIN_TOKEN_HERE"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    if TOKEN == "YOUR_ADMIN_TOKEN_HERE":
        print("\n   ℹ️  Saltando tests de admin (no hay token configurado)")
        return
    
    # 1. Listar todas las propiedades
    print("\n1️⃣  GET /api/properties/ (CON TOKEN DE ADMIN)")
    response = requests.get(f"{BASE_URL}/api/properties/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Éxito: {len(response.json())} propiedades encontradas")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 2. Listar propiedades ocupadas
    print("\n2️⃣  GET /api/properties/?rental_status=occupied (CON TOKEN DE ADMIN)")
    response = requests.get(f"{BASE_URL}/api/properties/?rental_status=occupied", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Éxito: {len(response.json())} propiedades ocupadas")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 3. Ver información financiera
    print("\n3️⃣  GET /api/properties/1/financials/ (CON TOKEN DE ADMIN)")
    response = requests.get(f"{BASE_URL}/api/properties/1/financials/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Éxito: Información financiera obtenida")
        print(f"   Balance: {response.json().get('balance')}")
    else:
        print(f"   ⚠️  Info: {response.text}")


def test_property_detail_public():
    """Probar acceso público a detalles de propiedad disponible"""
    print("\n" + "="*80)
    print("🔍 TEST: Detalle público de propiedad disponible")
    print("="*80)
    
    # Primero obtener una propiedad disponible
    print("\n1️⃣  Obteniendo ID de propiedad disponible...")
    response = requests.get(f"{BASE_URL}/api/properties/?rental_status=available")
    
    if response.status_code != 200 or not response.json():
        print("   ⚠️  No hay propiedades disponibles para probar")
        return
    
    property_id = response.json()[0]['id']
    property_name = response.json()[0]['name']
    print(f"   Propiedad encontrada: ID={property_id}, Nombre='{property_name}'")
    
    # Ver detalle sin autenticación
    print(f"\n2️⃣  GET /api/properties/{property_id}/ (SIN TOKEN)")
    response = requests.get(f"{BASE_URL}/api/properties/{property_id}/")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Éxito: Detalle obtenido")
        print(f"\n   📋 Campos incluidos:")
        print(f"      - name: {data.get('name')}")
        print(f"      - address: {data.get('address')}")
        print(f"      - details: {'✅' if data.get('details') else '❌'}")
        print(f"      - media: {'✅' if data.get('media') else '❌'}")
        print(f"      - inventory: {'✅' if data.get('inventory') else '❌'}")
        print(f"      - repairs: {'✅' if data.get('repairs') else '❌'}")
        
        print(f"\n   🔒 Campos OCULTOS para usuarios anónimos:")
        print(f"      - laws (regulaciones): {'❌ OCULTO' if 'laws' not in data else '⚠️ VISIBLE (ERROR)'}")
        
        # Verificar que no haya precios de enseres
        if data.get('inventory'):
            has_price = any('price' in item.get('enser', {}) for item in data['inventory'])
            print(f"      - precio de enseres: {'⚠️ VISIBLE (ERROR)' if has_price else '❌ OCULTO'}")
        
        # Verificar que no haya costos de reparaciones
        if data.get('repairs'):
            has_cost = any('cost' in repair for repair in data['repairs'])
            print(f"      - costo de reparaciones: {'⚠️ VISIBLE (ERROR)' if has_cost else '❌ OCULTO'}")
    else:
        print(f"   ❌ Error: {response.text}")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "🚀 "*20)
    print("PRUEBAS DE ACCESO A LA API DE PROPIEDADES")
    print("🚀 "*20)
    
    try:
        # 1. Tests de acceso público
        test_public_access()
        
        # 2. Tests de detalle de propiedad
        test_property_detail_public()
        
        # 3. Tests de acceso admin (opcional)
        test_admin_access()
        
        print("\n" + "="*80)
        print("✅ TESTS COMPLETADOS")
        print("="*80)
        print("\nREVISA los resultados para verificar que todo funciona correctamente.")
        print("Los accesos públicos deben retornar 200 OK")
        print("Los accesos bloqueados deben retornar 401 Unauthorized")
        
    except requests.exceptions.ConnectionError:
        print("\n" + "="*80)
        print("❌ ERROR: No se puede conectar al servidor")
        print("="*80)
        print("\nAsegúrate de que el servidor Django esté corriendo:")
        print("   python manage.py runserver")
        print("\nY que la URL base sea correcta:")
        print(f"   {BASE_URL}")


if __name__ == "__main__":
    main()
