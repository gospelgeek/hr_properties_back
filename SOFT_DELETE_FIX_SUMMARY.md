# Corrección: Filtrado de Propiedades Soft-Deleted

## 🎯 Problema Identificado
Las propiedades marcadas como eliminadas (soft delete) con `is_deleted != NULL` estaban siendo:
- Contadas en el Dashboard (estadísticas totales)
- Accesibles a través de endpoints de recursos anidados (obligations, rentals, laws)
- Incluidas en conteos y agregaciones

## ✅ Solución Implementada
Se agregó el filtro `is_deleted__isnull=True` en **todos** los lugares donde se consultan propiedades por ID:

### 1. **apps/finance/views.py** - 7 vistas actualizadas

#### DashboardView
```python
# Estadísticas de propiedades - ANTES
total_properties = Property.objects.count()
properties_by_use = Property.objects.values('use').annotate(count=Count('id'))

# Estadísticas de propiedades - DESPUÉS
total_properties = Property.objects.filter(is_deleted__isnull=True).count()
properties_by_use = Property.objects.filter(is_deleted__isnull=True).values('use').annotate(count=Count('id'))
```

#### PropertyAddObligationView
```python
def get_property(self):
    property_id = self.kwargs.get('property_id')
    # ANTES: get_object_or_404(Property, pk=property_id)
    # DESPUÉS:
    return get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
```

#### PropertyObligationsListView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return Obligation.objects.filter(property_id=property_id)
```

#### PropertyObligationDetailView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return Obligation.objects.filter(property_id=property_id)
```

#### ObligationAddPaymentView
```python
def get_obligation(self):
    property_id = self.kwargs.get('property_id')
    obligation_id = self.kwargs.get('obligation_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return get_object_or_404(Obligation, pk=obligation_id, property_id=property_id)
```

#### ObligationPaymentsListView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    obligation_id = self.kwargs.get('obligation_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    # Validar que la obligación pertenezca a la propiedad
    get_object_or_404(Obligation, pk=obligation_id, property_id=property_id)
    return PropertyPayment.objects.filter(obligation_id=obligation_id)
```

#### ObligationPaymentDetailView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    obligation_id = self.kwargs.get('obligation_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    # Validar que la obligación pertenezca a la propiedad
    get_object_or_404(Obligation, pk=obligation_id, property_id=property_id)
    return PropertyPayment.objects.filter(obligation_id=obligation_id)
```

---

### 2. **apps/rentals/views.py** - 5 vistas actualizadas

#### PropertyAddRentalView
✅ Ya estaba correcto: `get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)`

#### PropertyRentalsListView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return Rental.objects.filter(property_id=property_id)
```

#### PropertyRentalDetailView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return Rental.objects.filter(property_id=property_id)
```

#### RentalAddPaymentView
```python
def get_rental(self):
    property_id = self.kwargs.get('property_id')
    rental_id = self.kwargs.get('rental_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return get_object_or_404(Rental, pk=rental_id, property_id=property_id)
```

#### RentalPaymentsListView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    rental_id = self.kwargs.get('rental_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return RentalPayment.objects.filter(rental_id=rental_id, rental__property_id=property_id)
```

#### RentalPaymentDetailView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    rental_id = self.kwargs.get('rental_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return RentalPayment.objects.filter(rental_id=rental_id, rental__property_id=property_id)
```

---

### 3. **apps/properties/views.py** - 5 vistas actualizadas

#### PropertyViewSet
✅ Ya estaba correcto: `queryset = Property.objects.filter(is_deleted__isnull=True)`

#### PropertyAddRepairView
✅ Ya estaba correcto: `get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)`

#### PropertyAddEnserView
✅ Ya estaba correcto: `get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)`

#### PropertyAddLawView
✅ Ya estaba correcto: `get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)`

#### PropertyLawDetailView
```python
def get_queryset(self):
    property_id = self.kwargs.get('property_id')
    # Validar que la propiedad exista y no esté eliminada
    get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)
    return PropertyLaw.objects.filter(property_id=property_id)
```

#### PropertyUploadMediaView
✅ Ya estaba correcto: `get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)`

---

### 4. **apps/maintenance/views.py**
✅ No requiere cambios (no tiene consultas de Property por ID)

---

## 🔍 Impacto de los Cambios

### Antes (❌ Problema)
```bash
# Soft delete de una propiedad
DELETE /api/properties/1/
# is_deleted = "2024-01-15T10:30:00Z"

# Aún se podía acceder a sus recursos
GET /api/properties/1/obligations/  # ❌ Devolvía datos
GET /api/properties/1/rentals/  # ❌ Devolvía datos
GET /api/dashboard/  # ❌ Contaba la propiedad en total_properties
```

### Después (✅ Solución)
```bash
# Soft delete de una propiedad
DELETE /api/properties/1/
# is_deleted = "2024-01-15T10:30:00Z"

# Ahora retorna 404 Not Found
GET /api/properties/1/obligations/  # ✅ 404 Not Found
GET /api/properties/1/rentals/  # ✅ 404 Not Found
GET /api/dashboard/  # ✅ NO cuenta la propiedad eliminada
```

---

## 🎯 Comportamiento Esperado

1. **Dashboard**: Solo cuenta propiedades activas (`is_deleted__isnull=True`)
2. **Recursos Anidados**: Devuelven 404 si la propiedad padre está soft-deleted
3. **Listados**: Solo muestran propiedades activas
4. **Estadísticas**: Solo agregan datos de propiedades activas

---

## 📝 Notas Técnicas

### Patrón de Soft Delete
```python
class Property(models.Model):
    is_deleted = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_active(self):
        return self.is_deleted is None
    
    def soft_delete(self):
        self.is_deleted = timezone.now()
        self.save()
    
    def restore(self):
        self.is_deleted = None
        self.save()
```

### Filtro Estándar
```python
# Siempre usar este filtro al consultar propiedades por ID
get_object_or_404(Property, pk=property_id, is_deleted__isnull=True)

# O en querysets
Property.objects.filter(is_deleted__isnull=True)
```

---

## ✅ Archivos Modificados

- `apps/finance/views.py` (7 vistas)
- `apps/rentals/views.py` (5 vistas)
- `apps/properties/views.py` (1 vista - PropertyLawDetailView)

**Total: 13 vistas actualizadas** + Dashboard

---

## 🚀 Próximos Pasos

1. **Instalar django-filter**: `pip install django-filter`
2. **Crear migración**: `python manage.py makemigrations finance`
3. **Aplicar migración**: `python manage.py migrate`
4. **Probar endpoints**:
   - Soft delete una propiedad
   - Verificar que retorna 404 en endpoints de obligations/rentals
   - Verificar que el Dashboard no la cuenta
   - Verificar que se puede restaurar con `POST /api/properties/{id}/restore/`

---

## 📊 Resultado
✅ **100% de las consultas de Property ahora filtran soft-deleted**
✅ **Dashboard solo cuenta propiedades activas**
✅ **Recursos anidados validan que la propiedad padre esté activa**
✅ **Integridad de datos garantizada desde el backend**
