"""
Filtros personalizados para Finance app

Permite filtrado avanzado en endpoints:
- Búsqueda por texto
- Rangos de fechas
- Rangos de montos
- Filtros por relaciones
"""
import django_filters
from .models import Obligation, PropertyPayment, Notification


class ObligationFilter(django_filters.FilterSet):
    """
    Filtros para obligaciones
    
    Ejemplos de uso:
    
    1. Por rango de fechas:
       GET /api/obligations/?due_date_from=2026-02-01&due_date_to=2026-02-28
    
    2. Por rango de montos:
       GET /api/obligations/?amount_min=100000&amount_max=500000
    
    3. Búsqueda en nombre de entidad:
       GET /api/obligations/?entity_contains=luz
    
    4. Filtros exactos:
       GET /api/obligations/?temporality=monthly&property=2
    
    5. Combinados:
       GET /api/obligations/?property=2&due_date_from=2026-02-01&amount_min=50000
    """
    
    # Rango de fechas de vencimiento
    due_date_from = django_filters.DateFilter(
        field_name='due_date', 
        lookup_expr='gte',
        label='Fecha de vencimiento desde'
    )
    due_date_to = django_filters.DateFilter(
        field_name='due_date', 
        lookup_expr='lte',
        label='Fecha de vencimiento hasta'
    )
    
    # Rango de montos
    amount_min = django_filters.NumberFilter(
        field_name='amount', 
        lookup_expr='gte',
        label='Monto mínimo'
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount', 
        lookup_expr='lte',
        label='Monto máximo'
    )
    
    # Búsqueda parcial en nombre de entidad
    entity_contains = django_filters.CharFilter(
        field_name='entity_name', 
        lookup_expr='icontains',
        label='Contiene en nombre de entidad'
    )
    
    class Meta:
        model = Obligation
        fields = {
            'temporality': ['exact'],
            'obligation_type': ['exact'],
            'property': ['exact'],
        }


class PropertyPaymentFilter(django_filters.FilterSet):
    """
    Filtros para pagos de obligaciones
    
    Ejemplos:
    GET /api/properties/2/obligations/1/payments/?date_from=2026-01-01&date_to=2026-01-31
    GET /api/properties/2/obligations/1/payments/?payment_method=1&amount_min=50000
    """
    
    # Rango de fechas de pago
    date_from = django_filters.DateFilter(
        field_name='date', 
        lookup_expr='gte',
        label='Fecha de pago desde'
    )
    date_to = django_filters.DateFilter(
        field_name='date', 
        lookup_expr='lte',
        label='Fecha de pago hasta'
    )
    
    # Rango de montos
    amount_min = django_filters.NumberFilter(
        field_name='amount', 
        lookup_expr='gte',
        label='Monto mínimo'
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount', 
        lookup_expr='lte',
        label='Monto máximo'
    )
    
    class Meta:
        model = PropertyPayment
        fields = {
            'payment_method': ['exact'],
            'obligation': ['exact'],
        }


class NotificationFilter(django_filters.FilterSet):
    """
    Filtros para notificaciones
    
    Ejemplos:
    GET /api/notifications/?is_read=false
    GET /api/notifications/?type=obligation_due&priority=high
    GET /api/notifications/?created_from=2026-02-01
    """
    
    # Rango de fechas de creación
    created_from = django_filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Creada desde'
    )
    created_to = django_filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Creada hasta'
    )
    
    class Meta:
        model = Notification
        fields = {
            'type': ['exact'],
            'priority': ['exact'],
            'is_read': ['exact'],
        }
