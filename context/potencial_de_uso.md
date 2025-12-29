# Reporte de Cobertura de Datos de Contexto (EM-DAT)

Este documento detalla el uso actual de los campos de la base de datos `public_emdat_custom_request_2025-12-04.xlsx` en la simulación TULIAN, confirmando la implementación de la Fase 4 (Hiper-Realismo).

## 1. Matriz de Cobertura

| Campo EM-DAT | Estado | Uso en Simulación |
| :--- | :--- | :--- |
| **Associated Types** | ✅ IMPLEMENTADO | Detecta "Food/Water shortage" para penalizar FCS/WASH. |
| **Event Name** | ✅ IMPLEMENTADO | Inyección narrativa (ej. "Hurricane Beta"). |
| **Origin** | ✅ IMPLEMENTADO | Inyección narrativa (ej. "Heavy rain"). |
| **AID Contribution** | ✅ IMPLEMENTADO | Modula la velocidad de recuperación post-desastre. |
| **Magnitude & Scale** | ✅ IMPLEMENTADO | Calcula probabilidad de destrucción física (Richter/Viento). |
| **Total Damage** | ✅ IMPLEMENTADO | Calcula Shock Económico y estrategias de afrontamiento. |
| **No. Homeless** | ✅ IMPLEMENTADO | Dispara probabilidad de Desplazamiento. |
| **No. Injured** | ✅ IMPLEMENTADO | Afecta preguntas de Salud. |
| **Total Affected** | ✅ IMPLEMENTADO | Índice base de impacto general. |
| **OFDA/Appeal/Decl.**| ✅ IMPLEMENTADO | Aumenta probabilidad de Asistencia Humanitaria. |
| **Admin Units** | ✅ IMPLEMENTADO | Filtrado geográfico preciso. |

---

## 2. Campos Intencionalmente Omitidos

Los siguientes campos han sido analizados y descartados por ahora debido a baja relevancia o complejidad técnica innecesaria:

*   **`Reconstruction Costs`**: Usamos `Total Damage` como proxy principal.
*   **`Insured Damage`**: Irrelevante para poblaciones vulnerables (target ODK).
*   **`CPI`**: No necesario para simulaciones de años recientes (2020-2025).
*   **`River Basin`**: Requiere motor GIS avanzado (fuera de alcance actual).
*   **`Location`**: Redundante con `Admin Units` (que es más estructurado).
*   **Metadatos (DisNo, Entry Date)**: Sin valor para la simulación.

*   **Económicos Adicionales**:
    *   `Reconstruction Costs` / `Adjusted`: Costos a largo plazo. Útil solo si simulamos recuperación a >2 años.
    *   `Insured Damage`: Daños cubiertos por seguros. Podría servir para simular hogares de clase alta, pero es raro en poblaciones vulnerables típicas de ODK humanitario.
    *   `CPI` (Consumer Price Index): Útil para ajustar la inflación si simulamos eventos antiguos (ej. 2005) y queremos proyectar costos a valor presente.

*   **Geográficos / Hidrológicos**:
    *   `River Basin`: Cuenca del río. Potencial para cruzar con mapas hidrológicos, pero complejo de implementar sin GIS.
    *   `Latitude` / `Longitude`: Centroide del evento. Ya está parcialmente cubierto por `Admin Units`, pero podría usarse para "desastres puntuales".

*   **Metadatos y Clasificación**:
    *   `DisNo.`, `External IDs`, `Entry Date`, `Last Update`: Metadatos administrativos. Sin valor para la simulación narrativa.
    *   `Classification Key`, `Disaster Group/Subgroup`: Redundantes con `Disaster Type` y `Subtype`, que ya usamos.

*   **Valores Booleanos/Flags**:
    *   `Historic`, `AA related`: Indicadores internos de la base de datos (Academic/History). Generalmente "No". Poco valor predictivo.

