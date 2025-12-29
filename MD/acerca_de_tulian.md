# Acerca de TULIAN (v1.2)

> **Última actualización:** Diciembre 2025

## ¿Qué es?

TULIAN es un simulador de encuestas ODK para seguridad alimentaria. Genera datos sintéticos realistas usando contexto de desastres (EM-DAT) y reglas del formulario ODK.

---

## ¿Para quién?

- Organizaciones humanitarias (WFP, ONG)
- Analistas de datos y M&E
- Desarrolladores de sistemas ODK
- Equipos que necesitan datos de prueba realistas

---

## Proceso de Simulación

```
1. Cargar ODK    → Parser extrae preguntas, choices, constraints, relevant
2. Seleccionar   → País(es) + Rango de años
3. Generar       → Datos respetando reglas ODK + contexto desastres
4. Analizar      → Dashboard con 7 indicadores WFP
5. Exportar      → CSV en orden exacto del ODK
```

---

## Reglas ODK Respetadas

| Regla | Descripción |
|-------|-------------|
| **Orden** | Campos en mismo orden que el survey |
| **Choices** | Solo valores permitidos de la hoja choices |
| **Constraints** | ✅ Validaciones estrictas ODK (ej: HHSize 0-11, Gastos 0-25) |
| **Relevant** | ✅ Lógica avanzada (incluye sub-módulos anidados y strings) |

---

## Capacidades Avanzadas de Simulación (v1.2)

### 1. Clima y Desastres
- **Filtro Regional Inteligente**: Detecta eventos nacionales incluso si la granularidad administrativa (ADM1/ADM2) difiere.
- **Probabilidad Dinámica**: 85% de probabilidad de reportar afectación climática (`HHAffectedClimate=1`) si hubo eventos reales.
- **Sub-módulos Completos**: Generación de todos los campos de detalle (inundaciones, sequías, tormentas).

### 2. Economía y Gastos
- **Diversidad de Datos**: Aumento de probabilidad de respuestas de compra (65%) para poblar métricas de `NonFoodConsumption`.
- **Integridad Negocio**: Impacto de desastres limitado (max 90%) para evitar gastos negativos o cero.
- **Validación Rango**: Parseo automático de constraints ODK (`.>=0 and .<=25`) para cada campo numérico.

### 3. Seguridad Alimentaria (HHS)
- **Consistencia Temporal**: Frecuencias (`_FR`) generadas consistentemente cuando la respuesta base es afirmativa.

### 4. Multi-País y Comparativas (Nuevo en v1.2)
- **Selector de Mapa Interactivo**: Selección visual de países directamente en el mapa.
- **Análisis Comparativo**: Insights automáticos comparando múltiples países.
- **Verificación de Exportación**: Vista previa del orden de campos antes de exportar CSV.

---

## Indicadores WFP

| Indicador | Descripción | Interpretación |
|-----------|-------------|----------------|
| **FCS** | Food Consumption Score | Pobre ≤21, Límite 21.5-35, Aceptable >35 |
| **rCSI** | Reduced Coping Strategy | Menor = Mejor |
| **LhCSI** | Livelihood Coping | None → Stress → Crisis → Emergency |
| **HHS** | Household Hunger Scale | Afirmativo = hambre severa |
| **FES** | Food Expenditure Share | ≥75% = Pobre |
| **ECMEN** | Economic Capacity | Adecuado/Límite/Pobre |
| **CARI** | Consolidated Approach | Combina los demás |

---

## Progresión de 4 Años

| Año | Progreso | Descripción |
|-----|----------|-------------|
| 0 | 0% | Baseline - Crisis |
| 1 | 60% | Asistencia humanitaria |
| 2 | 90% | Consolidación |
| 3+ | 100% | Sostenibilidad |

---

## Contexto de Desastres (EM-DAT)

Los datos de simulación se ajustan según eventos reales:
- Tipo de desastre (inundación, sequía, tormenta)
- Magnitud (escala Richter, velocidad viento)
- Personas afectadas
- Daño económico
- Respuesta humanitaria (OFDA, apelaciones)

> 📖 Ver documentación completa: [Contextualización de Datos](contextualizacion_de_datos.md)

---

## Estructura del Proyecto

```
TULIAN/
├── backend/         # API FastAPI + Motor de simulación
├── frontend/        # Interfaz React + Vite
├── scripts/         # Scripts de utilidad y análisis
├── tests/           # Scripts de verificación
├── context/         # Datos EM-DAT
├── ODK/             # Archivos XLSForm
├── MD/              # Documentación
└── output/          # Archivos generados (ignorado en git)
```

---

## Tecnología

- **Backend**: Python 3.12, FastAPI, Pandas
- **Frontend**: React 18, Vite, TailwindCSS, Recharts, Leaflet
- **Datos**: EM-DAT, XLSForm

---

## Repositorio

**GitHub**: [Geopoldo/simulator](https://github.com/Geopoldo/simulator)
