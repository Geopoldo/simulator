# Documentación Técnica Detallada: Lógica y Adaptabilidad

Este documento profundiza en **cómo funciona TULIAN internamente**, desglosando los algoritmos de simulación, la integración de contexto (Hiper-Realismo) y la arquitectura agnóstica para adaptarse a cualquier formulario ODK.

## 1. Arquitectura del Motor de Simulación

El núcleo del sistema es `simulator.py`, que opera como una máquina de estados para cada "encuestado" simulado.

### A. El Loop de Encuesta
A diferencia de los generadores de datos aleatorios tradicionales, TULIAN no genera columnas independientes. Simula la experiencia lineal de un encuestador:

1.  **Inicialización del Hogar**: Se crea un `context` base con atributos demográficos (Tamaño, Ubicación Admin1) derivados de `profiles.py`.
2.  **Recorrido Secuencial**: Itera sobre la lista de preguntas del ODK (`survey`) en orden.
3.  **Evaluación de Relevancia (`Relevant`)**:
    *   Para cada pregunta, el sistema evalúa la expresión ODK `relevant` (ej. `${gender} = 'female'`).
    *   Utiliza un parser personalizado en `rules.py` que soporta sintaxis ODK estándar.
    *   Si la condición no se cumple, la pregunta se salta (valor `NULL`), replicando el comportamiento real de ODK Collect.
4.  **Generación de Valor**: Si es relevante, se genera una respuesta basada en el **Contexto Acumulado** (respuestas anteriores + contexto externo).
5.  **Validación (`Constraint`)**: El valor generado se prueba contra la expresión `constraint`. Si falla, se regenera hasta 10 veces (lógica de reintento).

---

## 2. Lógica de Contexto e Hiper-Realismo (Fases 1-4)

TULIAN enriquece los datos inyectando variables externas de **EM-DAT** y lógica de negocio humanitario.

### A. Contexto Temporal y Geográfico (Fase 1)
*   **Año del Evento**: El sistema elige un año para la encuesta. Si hubo desastres en ese año (según EM-DAT), se activan flags de "Año de Crisis".
*   **Filtro Admin1**: Solo los hogares ubicados en departamentos afectados por el evento (según `Admin Units` de EM-DAT) sufren los efectos.

### B. Severidad y Respuesta (Fase 2)
*   **Probabilidad de Asistencia**:
    *   Base: 15%.
    *   Si el desastre tuvo `OFDA Response`, `Appeal` o `Declaration`: Se suma +35%, +20%, +15% respectivamente.
    *   *Resultado*: En crisis mayores, la asistencia sube al 85-90%, reflejando el despliegue humanitario.

### C. Impacto Físico y Económico (Fase 3 & 4)
*   **Shock Económico**:
    *   $Damage > 1B USD$ -> Reduce el poder adquisitivo (Gasto en Alimentos) en un 30% y fuerza estrategias de afrontamiento (LhCSI) de "Emergencia".
*   **Destrucción Física (Hiper-Realismo)**:
    *   Se analiza la magnitud física (`Richter`, `Km/h`).
    *   *Sismo > 7.0* o *Viento > 200 Km/h*: Fuerza la respuesta "Casa Destruida" (House Destroyed) con una probabilidad fija (40-50%), anulando la aleatoriedad normal.
*   **Escasez Sectorial**:
    *   Si el evento es de tipo `"Food shortage"` (detectado en `Associated Types`), penaliza puntajes FCS adicionalmente.

### D. Narrativa Generativa (Fase 4)
*   El sistema inyecta el **Nombre Real del Evento** (campo `Event Name` de EM-DAT) y su **Origen** en los campos de texto libre (`Comments`), creando historias únicas como: *"We were hit by Hurricane Beta. We have no food left."*

---

## 3. Adaptabilidad a Cualquier ODK

TULIAN está diseñado para ser **agnóstico de la encuesta**. No está "hardcoded" para un solo formulario.

### ¿Cómo se adapta?

1.  **Parsing Dinámico**:
    *   Lee el archivo `.xlsx`, extrae las hojas `survey` y `choices`.
    *   Identifica tipos de preguntas (`integer`, `select_one`, `text`, `calculate`).

2.  **Detección de Semántica por Nombre**:
    *   Aunque funciona con cualquier variable, aplica "inteligencia especial" si detecta nombres estandarizados comunes en el sector humanitario (WFP/UNHCR):
        *   `FCS` (Food Consumption Score): Aplica lógica de dietas.
        *   `rCSI` / `LhCSI`: Aplica lógica de afrontamiento.
        *   `Exp`, `Cost`, `Purch`: Aplica modelos de gasto log-normales.
        *   `Lat`, `Lon`, `GPS`: Genera coordenadas dentro del bounding box del país (`profiles.py`).

3.  **Fallback Genérico**:
    *   Si encuentra una pregunta desconocida (ej. `favorite_color`), simplemente elige una opción aleatoria de su lista de `choices` o genera un string/entero genérico.
    *   **Esto garantiza que el simulador nunca falle**, sin importar qué preguntas extra traiga el formulario nuevo.

4.  **Extensibilidad**:
    *   Para soportar un nuevo país, solo se debe agregar una entrada en `profiles.py` con sus regiones y moneda. El resto de la lógica se adapta automáticamente.
