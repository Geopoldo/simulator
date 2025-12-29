# Contextualización de Datos Simulados en TULIAN

## Descripción General

TULIAN genera datos de encuestas ODK **contextualmente realistas** al combinar la estructura de un formulario ODK con datos reales de desastres de la base de datos **EM-DAT** (Emergency Events Database). Esto permite que las respuestas simuladas reflejen las condiciones humanitarias reales de un país en un período de tiempo específico.

---

## Arquitectura de 3 Capas

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 1: FUENTE DE DATOS                      │
│                context_loader.py + EM-DAT Excel                 │
│         (Base de datos de desastres naturales reales)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAPA 2: CÁLCULO DE IMPACTO                     │
│           simulation/disaster_impact.py + humanitarian.py       │
│              (Transforma datos en multiplicadores)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CAPA 3: GENERACIÓN SESGADA                      │
│                       simulator.py                              │
│     (Aplica multiplicadores a preguntas del ODK survey)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capa 1: Carga de Contexto (`context_loader.py`)

### Fuente de Datos

El sistema utiliza el archivo **EM-DAT** ubicado en `context/public_emdat_custom_request_2025-12-04.xlsx`, que contiene registros históricos de desastres naturales a nivel mundial.

### Campos Extraídos

| Campo EM-DAT | Campo Interno | Uso en Simulación |
|--------------|---------------|-------------------|
| `Country` | `Country_Norm` | Filtrado por país |
| `Start Year/Month/Day` | `start_date` | Cálculo de temporalidad |
| `End Year/Month/Day` | `end_date` | Duración del desastre |
| `Total Affected` | - | Base del impacto logarítmico |
| `Disaster Type` | - | Clasificación del evento |
| `Disaster Subtype` | `disaster_subtype` | Especificidad del desastre |
| `Magnitude` | `magnitude` | Severidad numérica |
| `Magnitude Scale` | `magnitude_scale` | Escala (Richter, km/h, Km²) |
| `OFDA/BHA Response` | `ofda_response` | Indicador de respuesta humanitaria |
| `Appeal` | `appeal` | Apelación internacional |
| `Declaration` | `declaration` | Declaración de emergencia |
| `No. Homeless` | `homeless` | Estimación de desplazados |
| `No. Injured` | `injured` | Impacto en salud |
| `Total Damage ('000 US$)` | `total_damage_usd` | Daño económico (convertido a USD) |
| `AID Contribution` | `aid_contribution_usd` | Ayuda recibida |
| `Associated Types` | `associated_shortages` | Escasez sectorial (comida, agua) |
| `Event Name` | `event_name` | Nombre para narrativas |
| `Origin` | `origin_desc` | Descripción del origen |

### Procesamiento

```python
# Ejemplo de extracción de eventos para Colombia
loader = ContextLoader("context/public_emdat_custom_request_2025-12-04.xlsx")
events = loader.get_events_by_country("Colombia")

# Cada evento incluye:
# - Fechas calculadas (start_date, end_date)
# - Duración en días (duration_days)
# - Campos normalizados para cálculos
```

---

## Capa 2: Cálculo de Impacto

### 2.1 Impacto Mejorado (`calculate_enhanced_impact`)

La función principal combina múltiples factores para calcular un **multiplicador de impacto total**:

```
total_impact = base_impact × magnitude_mult × temporal_mult × severity_mult × sectorial_penalty
```

#### Componentes:

| Factor | Fórmula | Rango |
|--------|---------|-------|
| **Base Impact** | `log₁₀(Total Affected) × 0.5` | 0.5 - 4.0 |
| **Magnitude Mult** | Según escala y umbrales | 1.0 - 2.0 |
| **Temporal Mult** | Decae en 12 meses | 0.0 - 1.5 |
| **Severity Mult** | `1.0 + 0.25 × severity_score` | 1.0 - 1.75 |
| **Sectorial Penalty** | +25% si hay "Food shortage" | 1.0 - 1.25 |

### 2.2 Multiplicador de Magnitud (`get_magnitude_multiplier`)

Los umbrales están configurados en `config/simulation_params.yaml`:

| Escala | Umbral Bajo | Umbral Alto | Multiplicador |
|--------|-------------|-------------|---------------|
| **Richter** (terremotos) | 5.0 | 7.0 | 1.2 - 2.0 |
| **km/h** (huracanes) | 120 | 180 | 1.3 - 2.0 |
| **Km²** (incendios) | 1000 | 10000 | 1.2 - 1.8 |
| **Kph** (tornados) | 150 | 250 | 1.3 - 2.0 |

### 2.3 Impacto Temporal (`calculate_temporal_impact`)

El impacto de un desastre **decae naturalmente** con el tiempo:

```
Meses desde evento    Factor de Recencia
       0-3           →    1.0 (impacto completo)
       3-12          →    1.0 → 0.0 (decae linealmente)
       >12           →    0.0 (impacto mínimo)
```

#### Modulación por Ayuda Recibida:

La velocidad de decaimiento se ajusta según la proporción `ayuda / daño`:

| Ratio Ayuda/Daño | Velocidad de Decaimiento |
|------------------|--------------------------|
| > 50% | 2.0× (recuperación rápida) |
| 10-50% | 1.0× (normal) |
| < 10% | 0.5× (recuperación lenta) |

#### Factor de Duración:

Los desastres prolongados tienen más impacto:

| Duración | Factor |
|----------|--------|
| > 365 días | 1.5× |
| 180-365 días | 1.3× |
| 90-180 días | 1.1× |
| < 90 días | 1.0× |

### 2.4 Score de Severidad (`calculate_severity_score`)

Suma de indicadores oficiales (0-3):

- **+1** si `OFDA/BHA Response = "Yes"`
- **+1** si `Appeal = "Yes"`
- **+1** si `Declaration = "Yes"`

---

## Capa 3: Generación Sesgada (`simulator.py`)

### Proceso de Simulación

1. **Selección de Año**: Prioriza años con eventos registrados
2. **Filtrado de Eventos**: Solo eventos del año seleccionado
3. **Cálculo de Impacto**: Usa funciones de Capa 2
4. **Generación de Respuestas**: Sesga valores según impacto

### Campos Afectados por Contexto

| Campo ODK | Efecto del Impacto Alto |
|-----------|-------------------------|
| `FCSStap` (consumo de alimentos básicos) | Valores más bajos (1-4 vs 5-7) |
| `rCSI` (estrategias de afrontamiento) | Valores más altos |
| `ReceivedAssistance` | Mayor probabilidad de "Yes" |
| `Displaced` | Mayor probabilidad si hay `homeless` |
| `LCS_Status` | Sesgo hacia "Crisis"/"Emergency" |
| `FoodExp_Purch` | Reducido por shock económico |
| `HHAffectedClimate` | Mayor probabilidad de "Yes" |

### Probabilidades Calculadas

#### Asistencia Humanitaria (`calculate_assistance_probability`)

| Indicadores Presentes | Probabilidad Base |
|-----------------------|-------------------|
| Ninguno | 15% |
| OFDA Response | +20% |
| Appeal | +25% |
| Declaration | +25% |
| **Máximo (todos)** | **85%** |

#### Desplazamiento (`check_displacement`)

| Total Homeless | Probabilidad |
|----------------|--------------|
| 0 | 0% |
| 1-1,000 | 10% |
| 1,000-5,000 | 30% |
| 5,000-10,000 | 45% |
| > 10,000 | 60% |

#### Shock Económico (`calculate_economic_shock`)

Escala logarítmica del daño total:

| Daño Total (USD) | Nivel de Shock |
|------------------|----------------|
| $1 millón | 0.2 |
| $10 millones | 0.4 |
| $100 millones | 0.6 |
| $1 billón | 0.8 |
| $10 billones | 1.0 |

---

## Flujo de Ejemplo

```
ENTRADA:
  País: Colombia
  Año: 2023

PASO 1 - context_loader:
  → Encuentra: Inundación en Enero 2023
    - Total Affected: 50,000
    - Magnitude: 8.2 (escala de área Km²)
    - OFDA Response: Yes
    - Homeless: 3,500

PASO 2 - disaster_impact:
  → base_impact = log₁₀(50,000) × 0.5 = 2.35
  → magnitude_mult = 1.8 (área grande afectada)
  → temporal_mult = 0.9 (evento de hace 6 meses)
  → severity_mult = 1.25 (OFDA presente)
  → TOTAL IMPACT = 2.35 × 1.8 × 0.9 × 1.25 = 4.76

PASO 3 - simulator:
  → FCSStap: 3 (reducido de 5-7 normal)
  → rCSI: 8 (aumentado de 2-4 normal)
  → ReceivedAssistance: "Yes" (probabilidad 35%)
  → Displaced: "Yes" (probabilidad 30%)
  → Comments: "Después de la inundación de enero, 
               nuestra situación empeoró..."

SALIDA:
  Registro de encuesta ODK con valores 
  contextualmente coherentes con la realidad 
  humanitaria de Colombia en 2023.
```

---

## Archivos Relacionados

| Archivo | Función |
|---------|---------|
| `backend/context_loader.py` | Carga y procesa datos EM-DAT |
| `backend/simulation/disaster_impact.py` | Cálculos de impacto de desastres |
| `backend/simulation/humanitarian.py` | Probabilidades humanitarias |
| `backend/simulator.py` | Generador principal de datos |
| `backend/config/simulation_params.yaml` | Parámetros configurables |
| `context/public_emdat_custom_request_2025-12-04.xlsx` | Base de datos EM-DAT |

---

## Ventajas del Sistema

1. **Realismo Basado en Datos**: Los desastres no son inventados, provienen de EM-DAT
2. **Temporalidad Inteligente**: El impacto decae naturalmente con el tiempo
3. **Respuesta Humanitaria Dinámica**: La probabilidad de asistencia refleja indicadores reales
4. **Shock Económico Proporcional**: Daño total afecta gastos simulados
5. **Narrativas Contextuales**: Los comentarios mencionan eventos reales
6. **Configuración Flexible**: Umbrales ajustables vía YAML

---

*Última actualización: Diciembre 2024*
