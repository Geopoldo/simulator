# Manual de Usuario - TULIAN

## Inicio Rápido

1. **Abrir**: http://localhost:5505
2. **Cargar**: Pestaña 1 → Subir archivo XLSForm
3. **Simular**: Pestaña 2 → Seleccionar países y años
4. **Analizar**: Pestaña 3 → Ver gráficos y exportar CSV

---

## Pestaña 1: Cargar ODK

1. Clic en "Seleccionar archivo"
2. Elegir archivo `.xlsx` (XLSForm)
3. Ver estructura parseada (preguntas, tipos, reglas)

> **Archivo de ejemplo**: `ODK/HFA + CARI (FES) + HHS + climate shocks and SEI checked.xlsx`

---

## Pestaña 2: Simular

### Configuración

| Campo | Descripción |
|-------|-------------|
| Países | Seleccionar uno o más en el mapa |
| Año inicio | Primer año de simulación (ej: 2020) |
| Año fin | Último año de simulación (ej: 2023) |
| Registros | Cantidad por país por año |

### Generar

1. Clic en "Simular"
2. Esperar generación (puede tardar según cantidad)
3. Ver mensaje de éxito con total de registros

---

## Pestaña 3: Analizar

### Dashboard

- **Mapa**: Ubicación de hogares por FCS
- **Gráficos**: 7 indicadores WFP (FCS, rCSI, LhCSI, HHS, FES, ECMEN, CARI)
- **Tabla**: Datos crudos con filtros

### Exportar CSV

1. Seleccionar países a exportar
2. Clic en botón "Export"
3. Archivo descargado con orden ODK exacto

---

## Pestaña 4: Acerca de

Guía de indicadores con:
- Descripción de cada indicador
- Fórmulas de cálculo WFP
- Interpretación de valores
- Proceso de simulación

---

## Tips

- ✅ Los datos se generan en el **mismo orden del ODK**
- ✅ Los campos con `relevant` no cumplido se **omiten** (comportamiento correcto)
- ✅ El **baseline (Año 1)** muestra hogares más vulnerables
- ✅ La **progresión** mejora en años siguientes
