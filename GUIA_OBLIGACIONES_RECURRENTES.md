# 📋 Sistema de Obligaciones Recurrentes - Análisis y Soluciones

## 🔍 Situación Actual

### ¿Cómo funciona ahora?

Actualmente, cada **Obligation** es un **registro único** que representa **UN SOLO PERÍODO** de pago:

```python
# Ejemplo: Cuota del banco de febrero
Obligation(
    property=mi_propiedad,
    entity_name="Banco Santander",
    amount=580000.00,
    due_date="2026-02-15",
    temporality="monthly"  # Indica que ES mensual, pero NO se crea automáticamente
)
```

### El Problema

Si tienes una obligación mensual (cuota bancaria, servicio, etc.) que debes pagar **todos los meses**:

❌ **Debes crear manualmente** una nueva obligación cada mes
❌ Si olvidas crearla, no aparecerá en el dashboard
❌ No hay alertas automáticas para esa obligación
❌ Mucho trabajo manual repetitivo

---

## 💡 Soluciones Propuestas

### Opción 1: Command para Generar Obligaciones del Próximo Mes ⭐ RECOMENDADO

**Ventaja**: Simple, controlado, fácil de implementar.

**Funcionamiento**:
1. Cada fin de mes, ejecutas un comando manualmente o por tarea programada
2. El comando busca todas las obligaciones del mes **actual**
3. Si tienen `temporality != 'one_time'`, crea automáticamente la obligación del **próximo mes**

**Implementación**:

```bash
# Crear comando Django
python manage.py create_next_month_obligations
```

**Código** (`apps/finance/management/commands/create_next_month_obligations.py`):

```python
from django.core.management.base import BaseCommand
from apps.finance.models import Obligation
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Genera automáticamente las obligaciones recurrentes del próximo mes'

    def handle(self, *args, **options):
        today = date.today()
        
        # Obtener obligaciones del mes actual que NO son one_time
        current_month_start = today.replace(day=1)
        next_month_start = current_month_start + relativedelta(months=1)
        
        # Buscar obligaciones recurrentes de este mes
        obligations = Obligation.objects.filter(
            due_date__gte=current_month_start,
            due_date__lt=next_month_start
        ).exclude(temporality='one_time')
        
        created_count = 0
        
        for obligation in obligations:
            # Calcular nueva fecha de vencimiento
            if obligation.temporality == 'monthly':
                new_due_date = obligation.due_date + relativedelta(months=1)
            elif obligation.temporality == 'bimonthly':
                new_due_date = obligation.due_date + relativedelta(months=2)
            elif obligation.temporality == 'quarterly':
                new_due_date = obligation.due_date + relativedelta(months=3)
            elif obligation.temporality == 'biannual':
                new_due_date = obligation.due_date + relativedelta(months=6)
            elif obligation.temporality == 'annual':
                new_due_date = obligation.due_date + relativedelta(years=1)
            elif obligation.temporality == 'weekly':
                new_due_date = obligation.due_date + timedelta(weeks=1)
            else:
                continue
            
            # Verificar que no exista ya
            exists = Obligation.objects.filter(
                property=obligation.property,
                entity_name=obligation.entity_name,
                due_date=new_due_date
            ).exists()
            
            if not exists:
                # Crear nueva obligación
                Obligation.objects.create(
                    property=obligation.property,
                    obligation_type=obligation.obligation_type,
                    entity_name=obligation.entity_name,
                    amount=obligation.amount,
                    due_date=new_due_date,
                    temporality=obligation.temporality
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Creada: {obligation.entity_name} - {new_due_date}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {created_count} obligaciones creadas')
        )
```

**Uso**:

```bash
# Ejecutar manualmente (últimos días del mes)
python manage.py create_next_month_obligations

# O programar en Windows Task Scheduler para ejecutar automáticamente
# cada día 25 del mes
```

---

### Opción 2: Modelo RecurringObligation (Más Complejo)

**Ventaja**: Más robusto, centralizado, con historial completo.

**Funcionamiento**:
1. Creas un **RecurringObligation** (template)
2. El sistema genera automáticamente las **Obligation** individuales según la frecuencia
3. Puedes pausar/reanudar/editar la recurrencia

**Implementación**:

```python
# Nuevo modelo
class RecurringObligation(models.Model):
    """Template para obligaciones recurrentes"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    obligation_type = models.ForeignKey(ObligationType, on_delete=models.PROTECT)
    entity_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    temporality = models.CharField(max_length=100, choices=Obligation.TEMPORALITY_CHOICES)
    
    # Control de recurrencia
    start_date = models.DateField(verbose_name='Fecha inicial')
    end_date = models.DateField(null=True, blank=True, verbose_name='Fecha final')
    is_active = models.BooleanField(default=True)
    
    # Día del mes en que vence (ej: 15 para el día 15 de cada mes)
    day_of_month = models.IntegerField(default=1)
    
    # Relación con obligaciones generadas
    # (Obligation tendría un FK a RecurringObligation)

# Command para generar instancias
class Command(BaseCommand):
    def handle(self, *args, **options):
        today = date.today()
        
        # Para cada RecurringObligation activa
        for recurring in RecurringObligation.objects.filter(is_active=True):
            # Calcular próxima fecha de vencimiento
            # Verificar si ya existe
            # Crear si no existe
            pass
```

**Ventajas**:
- ✅ Puedes ver todas las obligaciones recurrentes en un solo lugar
- ✅ Puedes pausar/reanudar/modificar fácilmente
- ✅ Historial completo de todas las instancias generadas

**Desventajas**:
- ❌ Requiere migración de base de datos
- ❌ Más complejo de mantener
- ❌ Requiere actualizar el frontend

---

### Opción 3: Clonar Manualmente (Actual Mejorado)

**Ventaja**: Sin código adicional.

**Funcionamiento**:
1. En el frontend, agregar un botón "Duplicar para próximo mes"
2. Al hacer clic, crea una nueva obligación copiando los datos de la actual
3. Cambia automáticamente la fecha al próximo mes

**Implementación en Frontend** (React):

```javascript
const duplicateObligation = async (obligation) => {
  const nextMonth = new Date(obligation.due_date);
  nextMonth.setMonth(nextMonth.getMonth() + 1);
  
  const newObligation = {
    ...obligation,
    due_date: nextMonth.toISOString().split('T')[0],
    id: undefined  // Remover ID para crear nueva
  };
  
  await api.post('/api/finance/obligations/', newObligation);
};
```

**En Backend** (Django Admin):

```python
# apps/finance/admin.py
class ObligationAdmin(admin.ModelAdmin):
    actions = ['duplicate_for_next_month']
    
    def duplicate_for_next_month(self, request, queryset):
        for obligation in queryset:
            if obligation.temporality != 'one_time':
                # Calcular nueva fecha
                new_due_date = obligation.due_date + relativedelta(months=1)
                
                # Crear duplicado
                Obligation.objects.create(
                    property=obligation.property,
                    obligation_type=obligation.obligation_type,
                    entity_name=obligation.entity_name,
                    amount=obligation.amount,
                    due_date=new_due_date,
                    temporality=obligation.temporality
                )
        
        self.message_user(request, f"{queryset.count()} obligaciones duplicadas")
    
    duplicate_for_next_month.short_description = "Duplicar para próximo mes"
```

---

## 🎯 Recomendación

**Para empezar: Opción 1 (Command)**

1. **Rápido de implementar** (30 minutos)
2. **Funciona inmediatamente**
3. **Se puede automatizar** con Task Scheduler
4. **No requiere cambios en frontend**

**A futuro: Opción 2 (RecurringObligation)**

Si el sistema crece y tienes muchas obligaciones recurrentes, vale la pena implementar el modelo completo.

---

## 📦 Instalación de Opción 1 (RECOMENDADA)

### Paso 1: Instalar dependencia

```bash
pip install python-dateutil
```

### Paso 2: Crear el comando

Ya está incluido en el código arriba. Guardarlo en:
```
apps/finance/management/commands/create_next_month_obligations.py
```

### Paso 3: Probar

```bash
python manage.py create_next_month_obligations
```

### Paso 4: Automatizar (Opcional)

Crear script `create_obligations.bat`:

```batch
@echo off
cd C:\Users\ASUS\Desktop\Juanes\Monitoria\hr-properties
call venv\Scripts\activate.bat
python manage.py create_next_month_obligations >> logs/recurring_obligations.log 2>&1
```

Programar en Task Scheduler para ejecutar **cada día 25 del mes**.

---

## ❓ Preguntas Frecuentes

### ¿Qué pasa si cambio el monto de una obligación?
Las obligaciones ya creadas NO se actualizan automáticamente. Debes editarlas manualmente o eliminarlas y recrearlas.

### ¿Qué pasa si elimino una obligación recurrente?
Solo se elimina esa instancia específica. Las futuras se seguirán creando si ejecutas el comando.

### ¿Puedo tener diferentes montos cada mes?
Sí, después de crear la obligación automáticamente, puedes editarla manualmente para ajustar el monto.

### ¿El comando crea obligaciones de años anteriores?
No, solo crea del mes siguiente. No afecta el pasado.

---

## 📝 Próximos Pasos

1. **Decidir** qué opción implementar (Recomiendo Opción 1)
2. **Crear** el comando
3. **Probar** manualmente
4. **Automatizar** con Task Scheduler
5. **Monitorear** los logs para verificar que funciona

¿Tienes más preguntas? ¡Pregunta!
