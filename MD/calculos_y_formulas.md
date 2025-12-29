# Cálculos y Fórmulas - TULIAN

Este documento detalla las fórmulas usadas en la simulación y los gráficos del dashboard.

---

## Índices de Seguridad Alimentaria

### FCS - Food Consumption Score

```javascript
FCS = (FCSStap × 2) + (FCSPulse × 3) + (FCSDairy × 4) + (FCSPr × 4) + 
      (FCSVeg × 1) + (FCSFruit × 1) + (FCSFat × 0.5) + (FCSSugar × 0.5)
```

| Grupo | Campo | Peso |
|-------|-------|------|
| Cereales/Tubérculos | FCSStap | 2 |
| Legumbres | FCSPulse | 3 |
| Lácteos | FCSDairy | 4 |
| Proteína | FCSPr | 4 |
| Vegetales | FCSVeg | 1 |
| Frutas | FCSFruit | 1 |
| Grasas | FCSFat | 0.5 |
| Azúcar | FCSSugar | 0.5 |

**Clasificación WFP**:
- Pobre: ≤ 21
- Límite: 21.5 - 35
- Aceptable: > 35

---

### rCSI - Reduced Coping Strategy Index

```javascript
rCSI = (rCSILessQlty × 1) + (rCSIBorrow × 2) + (rCSIMealSize × 1) + 
       (rCSIMealAdult × 3) + (rCSIMealNb × 1)
```

| Estrategia | Campo | Peso |
|------------|-------|------|
| Comer alimentos menos preferidos | rCSILessQlty | 1 |
| Pedir prestado alimentos | rCSIBorrow | 2 |
| Reducir tamaño de porciones | rCSIMealSize | 1 |
| Adultos comen menos para niños | rCSIMealAdult | 3 |
| Reducir número de comidas | rCSIMealNb | 1 |

**Interpretación**: 0-56. Menor = Mejor.

---

### LhCSI - Livelihood Coping Strategies

```javascript
// Categorías por severidad
Stress:     Lcs_stress_Savings, Lcs_stress_BorrowCash, Lcs_stress_SoldHHAssets
Crisis:     Lcs_crisis_ProdAssets, Lcs_crisis_Health, Lcs_crisis_OutSchool
Emergency:  Lcs_em_ResAsset, Lcs_em_Begged, Lcs_em_IllegalAct

// Clasificación (una respuesta afirmativa asigna categoría)
if (Emergency.any == 1) return "Emergency"
if (Crisis.any == 1) return "Crisis"
if (Stress.any == 1) return "Stress"
return "None"
```

---

### FES - Food Expenditure Share

```javascript
// Suma de gastos en alimentos (campos HHExpF*_MN_*)
FoodExpenses = Σ HHExpFCer_Purch_MN_7D + HHExpFTub_Purch_MN_7D + ...

// Suma de gastos no alimentarios (campos HHExpNF*_MN_*)
NonFoodExpenses = Σ HHExpNFHyg_Purch_MN_1M + HHExpNFTransp_Purch_MN_1M + ...

// Porcentaje
FES = (FoodExpenses / (FoodExpenses + NonFoodExpenses)) × 100
```

**Clasificación WFP**:
- Pobre: ≥ 75%
- Límite: 65-74%
- Adecuado: < 65%

---

### CARI - Consolidated Approach for Reporting Indicators

```javascript
// Clasificar cada indicador en categorías 1-4
fcsClass = FCS <= 21 ? 4 : FCS <= 35 ? 3 : FCS <= 42 ? 2 : 1
rcsiClass = rCSI >= 19 ? 4 : rCSI >= 10 ? 3 : rCSI >= 4 ? 2 : 1
lhcsiClass = LhCSI == "Emergency" ? 4 : LhCSI == "Crisis" ? 3 : LhCSI == "Stress" ? 2 : 1
fesClass = FES >= 75 ? 4 : FES >= 65 ? 3 : FES >= 50 ? 2 : 1

// Promedio redondeado
average = (fcsClass + rcsiClass + lhcsiClass + fesClass) / 4

// Clasificación final
if (average >= 3.5) return "Severely Insecure"
if (average >= 2.5) return "Moderately Insecure"
if (average >= 1.5) return "Marginally Secure"
return "Food Secure"
```

---

## Simulación de Lugares

### Obtención de Coordenadas GPS

```python
# 1. Buscar desastres del país en EM-DAT con coordenadas
events = CONTEXT_LOADER.get_events_by_country(country_name)
events_with_coords = [e for e in events if e.get('Latitude') and e.get('Longitude')]

# 2. Si hay desastres, usar coordenadas cercanas
if events_with_coords:
    event = random.choice(events_with_coords)
    base_lat = event['Latitude']
    base_lon = event['Longitude']
    # Añadir variación aleatoria ±0.5 grados (~50km)
    lat = base_lat + random.uniform(-0.5, 0.5)
    lon = base_lon + random.uniform(-0.5, 0.5)

# 3. Si no hay desastres con coordenadas, usar perfil del país
elif country_profile.geopoint:
    lat = profile_lat + random.uniform(-0.1, 0.1)  # ±10km
    lon = profile_lon + random.uniform(-0.1, 0.1)

# 4. Fallback: usar Faker para generar coordenadas del país
else:
    fake = Faker(country_locale)
    lat, lon = fake.latlng()
```

### Regiones Administrativas (ADMIN0-5)

```python
# Obtener del perfil del país
profile = build_country_profile(country_name)

ADMIN0Name = country_name                        # País
ADMIN1Name = random.choice(profile['admin1'])    # Departamento/Estado
ADMIN2Name = random.choice(profile['admin2'])    # Municipio
ADMIN3Name = random.choice(profile['admin3'])    # Localidad
ADMIN4Name = random.choice(profile['streets'])   # Calle
ADMIN5Name = random.choice(profile['settlements'])  # Asentamiento
```

### Formato Geopoint ODK

```python
# El campo _Geopoint_value sigue el formato ODK: "lat lon altitude accuracy"
_Geopoint_value = f"{lat} {lon} 0 0"
```

---

## Progresión Temporal

### Curva de Mejora (4 años)

```yaml
# config/simulation_params.yaml
progression:
  year_0: 0.0    # Baseline: Crisis
  year_1: 0.6    # 60% mejora (asistencia)
  year_2: 0.9    # 90% mejora (consolidación)
  year_3_plus: 1.0  # 100% mejora (sostenibilidad)
```

### Aplicación a Indicadores

```python
progress = get_progress_factor(year_index)  # 0.0 a 1.0

# FCS mejora con el tiempo
fcs_value = base_fcs + (max_improvement * progress)

# rCSI disminuye con el tiempo
rcsi_value = base_rcsi * (1 - progress * 0.7)

# HHS solo afirmativo en año 0
if year_index > 0:
    hhs_value = 0  # No hambre
```

---

## Multiplicadores de Impacto de Desastres

```yaml
# config/simulation_params.yaml
disaster_impact:
  magnitude_multipliers:
    richter:
      - threshold: 7.0, multiplier: 2.0  # Catastrófico
      - threshold: 6.0, multiplier: 1.5  # Mayor
      - threshold: 5.0, multiplier: 1.2  # Moderado
    wind_speed:
      - threshold: 200, multiplier: 2.0  # Cat 5
      - threshold: 150, multiplier: 1.6  # Cat 4
      - threshold: 120, multiplier: 1.3  # Cat 3
```
