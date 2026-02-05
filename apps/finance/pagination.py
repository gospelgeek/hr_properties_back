"""
Paginación personalizada para la aplicación Finance
"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Paginación estándar para listados generales
    
    Uso:
    GET /api/obligations/?page=1
    GET /api/obligations/?page=2&page_size=50
    
    Parámetros:
    - page: Número de página (default: 1)
    - page_size: Tamaño de página (default: 20, max: 100)
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """
    Paginación para listados grandes (ej: historial de pagos)
    
    Uso:
    GET /api/property-payments/?page=1
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
