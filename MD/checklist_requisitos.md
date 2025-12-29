# Checklist de Requisitos - TULIAN

## ✅ Requisitos del Cliente

### 1. Orden de Datos
- [x] Las preguntas/variables están en el mismo orden que el ODK
- [x] Los datos se generan en orden preservando validaciones
- [x] Campos internos (`_events_summary`, `latitude`, `longitude`) al final

**Verificación**: ✅ 325 campos ODK en orden correcto

### 2. Valores de Choices
- [x] Los datos usan solo valores de la hoja `choices`
- [x] Validación implementada en `_pick_option()`

### 3. Constraints
- [x] Los datos respetan condiciones `constraint`
- [x] Loop de retry (hasta 10 intentos) si falla
- [x] **New:** Parseo automático de rangos complejos (ej. `.>=0 and .<11`)
- [x] **New:** Verificado HHSize (0-11) y Gastos (0-25)

### 4. Relevant
- [x] Los campos se omiten si `relevant` no se cumple
- [x] 103 campos correctamente omitidos por condiciones no cumplidas
- [x] **New:** Sub-módulos climáticos activados correctamente (filas 80-116)
- [x] **New:** Módulos de frecuencia HHS generados inconsistentemente arreglados

### 5. Progresión de Seguridad Alimentaria
- [x] Año 1: Baseline vulnerable (HHS afirmativo ~56%)
- [x] Años 2-4: Mejora progresiva (HHS 0%)
- [x] FCS mejora de 5.8 a 7.0
- [x] rCSI reduce de 3.9 a 1.7

---

## ✅ Requisitos del `simulated scores.docx`

### Indicadores
- [x] HHS → Solo afirmativo en Año 1
- [x] FCS → Mejora progresiva
- [x] rCSI → Disminuye con el tiempo
- [x] LhCSI → Influenciado por shock económico
- [x] FES → Gasto alimentos ~70% baseline

### Contexto
- [x] Choques coherentes con EM-DAT
- [x] Impacto de desastres influye en indicadores
- [x] Progresión de 4 años implementada

---

## ✅ Verificación de Campos

| Métrica | Valor |
|---------|-------|
| Campos ODK totales | 428 |
| Campos en simulación | 330 |
| Campos ODK presentes | 325 |
| Campos internos | 5 |
| **Todos en orden correcto** | ✅ |

---

## ✅ Funcionalidades Dashboard

- [x] 7 gráficos de indicadores WFP
- [x] Guía explicativa de indicadores
- [x] Exportación CSV en orden ODK
- [x] Mapa con ubicaciones GPS
- [x] Filtros por país

---

*Verificación: 29 de Diciembre, 2025*
