# Documentación del Sistema de Simulación y Contexto

Este documento describe la arquitectura y funcionamiento del motor de simulación de datos ODK integrado en la aplicación **TULIAN**.

## 1. Visión General

El sistema permite generar datos sintéticos realistas para encuestas ODK, utilizando perfiles estadísticos detallados por país y datos de contexto histórico (desastres naturales) para influir en los resultados.

### Componentes Clave

1.  **Backend (FastAPI)**: Orquestador de la simulación.
2.  **Motor de Simulación (`simulator.py`)**: Núcleo lógico que itera sobre la encuesta.
3.  **Perfiles de País (`profiles.py`)**: Base de conocimientos estadísticos (tamaño de hogar, gastos, geografía).
4.  **Motor de Reglas (`rules.py`)**: Evalúa lógica condicional (skip patterns) de ODK.
5.  **Contexto (`context_loader.py`)**: Carga datos históricos de EM-DAT.

---

## 2. Flujo de Simulación

El proceso de simulación sigue estos pasos:

1.  **Recepción de Solicitud**: El frontend envía la estructura del formulario (XLSForm convertido a JSON) y el país objetivo.
2.  **Carga de Contexto**:
    *   Se selecciona el perfil del país desde `profiles.py` (moneda, regiones, enumeradores).
    *   Se consultan los eventos de desastre (EM-DAT) para ese país.
3.  **Iteración de Hogares**:
    *   Para cada registro solicitado, se asigna un **Año** (influenciado por años con desastres en el historial).
    *   Se genera un **Perfil de Hogar** (tamaño, ubicación base).
4.  **Generación de Respuestas**:
    *   El simulador recorre pregunta por pregunta.
    *   **Evaluación de Relevancia**: Antes de responder, consulta a `rules.py` si la pregunta es relevante dados los valores anteriores (ej. *"¿Está embarazada?"* solo si *Género == Mujer*).
    *   **Generación de Valor**: Si es relevante, calcula el valor usando modelos matemáticos.

---

## 3. Lógica "Inteligente" y Contexto

A diferencia de un generador aleatorio simple, TULIAN aplica reglas de negocio:

### A. Influencia de Desastres
El sistema calcula un índice de impacto basado en la cantidad de desastres ocurridos en el año simulado.
*   **Seguridad Alimentaria (FCS)**: Los puntajes tienden a mejorar con el tiempo, pero sufren penalizaciones severas en años de desastre.
*   **Estrategias de Afrontamiento (rCSI)**: Aumentan (empeoran) durante crisis.
*   **Gastos**: Se reducen o redistribuyen en tiempos de crisis.

### B. Nuevas Lógicas de Contexto (Fases 2 y 3)
Se han integrado indicadores específicos de EM-DAT para refinar las probabilidades:

1.  **Severidad y Respuesta Humanitaria**:
    *   Si el desastre tuvo **Respuesta Internacional** (OFDA, Llamamiento, Declaración), la probabilidad de que los hogares reporten haber recibido asistencia aumenta drásticamente (hasta 85-90%).

2.  **Desplazamiento Forzado**:
    *   Eventos con alto número de personas "Sin Hogar" (>5000) incrementan la probabilidad de respuestas afirmativas en preguntas sobre **Desplazamiento** y problemas de **Alojamiento** (hasta un 60%).

3.  **Shock Económico (Economic Shock)**:
    *   Se calcula basado en el **Daño Total** (USD) del evento.
    *   Desastres con daños >$1B (mil millones) reducen el poder adquisitivo (Gastos) hasta un 30% y empujan las **Estrategias de Afrontamiento de Medios de Vida (LhCSI)** hacia categorías de "Crisis" y "Emergencia".

### C. Geografía Coherente
Utiliza polígonos y puntos geográficos definidos en `profiles.py` para generar coordenadas GPS válidas dentro del país. Además, mapea las divisiones administrativas (ej. Departamentos en Colombia) a los campos `ADMIN`.

### D. Diversidad Dinámica
*   **Preguntas de Selección Múltiple**: La cantidad de opciones seleccionadas varía según el "progreso" o riqueza simulada del hogar.
*   **Probabilidades Sí/No**: No son 50/50. Se ajustan según el tipo de pregunta (ej. compra de activos vs. deuda) y el contexto económico.

---

## 4. Archivos Clave

*   `backend/simulator.py`: Loop principal y lógica de orquestación.
*   `backend/profiles.py`: Datos estáticos de países (portado del sistema legado).
*   `backend/rules.py`: Evaluador de expresiones ODK (`${var} = 'val'`).
*   `backend/context_loader.py`: Lector de Excel de EM-DAT.

## 5. Extensión Futura

Para agregar un nuevo país:
1.  Editar `backend/profiles.py`.
2.  Registrar el nuevo país con `_register_country` definiendo sus parámetros (moneda, límites geográficos, regiones).
