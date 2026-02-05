"""
Permisos personalizados por roles
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permiso para verificar que el usuario tenga rol de admin.
    Los admins tienen acceso completo a todos los endpoints.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si el usuario tiene rol admin
        user_roles = request.user.userrole_set.values_list('role__name', flat=True)
        return 'admin' in user_roles


class IsClientUser(permissions.BasePermission):
    """
    Permiso para verificar que el usuario tenga rol de cliente.
    Los clientes solo tienen acceso de lectura a sus propios datos.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si el usuario tiene rol cliente
        user_roles = request.user.userrole_set.values_list('role__name', flat=True)
        
        # Solo permitir métodos seguros (GET, HEAD, OPTIONS) para clientes
        if 'cliente' in user_roles:
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsAdminOrReadOnlyClient(permissions.BasePermission):
    """
    Permiso combinado:
    - Admins: Acceso completo (CRUD)
    - Clientes: Solo lectura de sus propios datos
    - Invitados: Sin acceso
    
    Este permiso debe usarse en conjunto con filtros en los ViewSets
    para asegurar que los clientes solo vean sus propios datos.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_roles = request.user.userrole_set.values_list('role__name', flat=True)
        
        # Admin tiene acceso completo
        if 'admin' in user_roles:
            return True
        
        # Cliente solo puede leer
        if 'cliente' in user_roles:
            return request.method in permissions.SAFE_METHODS
        
        # Invitados no tienen acceso
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica permisos a nivel de objeto.
        Los clientes solo pueden ver sus propios datos.
        """
        user_roles = request.user.userrole_set.values_list('role__name', flat=True)
        
        # Admin puede ver todo
        if 'admin' in user_roles:
            return True
        
        # Cliente solo puede ver sus propios datos
        if 'cliente' in user_roles:
            # Solo métodos seguros
            if request.method not in permissions.SAFE_METHODS:
                return False
            
            # Verificar que el objeto pertenezca al cliente
            # Esto debe adaptarse según el modelo
            # Por ejemplo, si es un Rental, verificar que rental.tenant.user == request.user
            if hasattr(obj, 'tenant'):
                return obj.tenant.user == request.user
            
            # Si es el propio tenant
            if hasattr(obj, 'user'):
                return obj.user == request.user
        
        return False


'''
═══════════════════════════════════════════════════════════════════════
📝 USO DE PERMISOS EN VIEWSETS
═══════════════════════════════════════════════════════════════════════

1. SOLO ADMINS (Crear, editar, eliminar):
   
   from apps.users.permissions import IsAdminUser
   
   class PropertyViewSet(viewsets.ModelViewSet):
       permission_classes = [IsAdminUser]

2. ADMINS + CLIENTES (Clientes solo lectura):
   
   from apps.users.permissions import IsAdminOrReadOnlyClient
   
   class RentalViewSet(viewsets.ModelViewSet):
       permission_classes = [IsAdminOrReadOnlyClient]
       
       def get_queryset(self):
           queryset = Rental.objects.all()
           
           # Filtrar por rol
           user_roles = self.request.user.userrole_set.values_list('role__name', flat=True)
           
           if 'cliente' in user_roles:
               # Clientes solo ven sus propios rentals
               queryset = queryset.filter(tenant__user=self.request.user)
           
           return queryset

3. ACCESO PÚBLICO (Lista de propiedades disponibles):
   
   from rest_framework.permissions import AllowAny
   
   @action(detail=False, methods=['get'], permission_classes=[AllowAny])
   def available(self, request):
       # Cualquiera puede ver propiedades disponibles
       properties = Property.objects.filter(rentals__status='available')
       ...

═══════════════════════════════════════════════════════════════════════
🔒 REGLAS DE ACCESO POR ROL
═══════════════════════════════════════════════════════════════════════

ADMIN:
✅ Ver, crear, editar, eliminar: Todo
✅ Acceso a: Todas las propiedades, todos los rentals, todas las finanzas

CLIENTE:
✅ Ver (solo sus datos):
   - Sus rentals (donde tenant.user == request.user)
   - Sus pagos de obligaciones
   - Sus reparaciones
   - Sus enseres
   - Su multimedia
   - Propiedades disponibles (rentals con status='available')

❌ NO puede ver:
   - Balance general
   - Documentación legal de otras propiedades
   - Rentals de otros clientes
   - Datos financieros generales

❌ NO puede:
   - Crear
   - Editar
   - Eliminar

INVITADO:
❌ Sin acceso a la API

═══════════════════════════════════════════════════════════════════════
🎯 VIEWSETS QUE NECESITAN PERMISOS
═══════════════════════════════════════════════════════════════════════

SOLO ADMIN:
- PropertyViewSet (crear/editar propiedades)
- ObligationViewSet (gestión de obligaciones)
- DashboardView (estadísticas generales)

ADMIN + CLIENTE (con filtros):
- RentalViewSet (clientes ven solo sus rentals)
- PropertyPaymentViewSet (clientes ven solo sus pagos)
- RepairViewSet (clientes ven solo sus reparaciones)
- EnserViewSet (clientes ven solo sus enseres)
- PropertyMediaViewSet (clientes ven solo multimedia de sus propiedades)

PÚBLICO:
- PropertyViewSet.available (lista de propiedades disponibles)
'''
