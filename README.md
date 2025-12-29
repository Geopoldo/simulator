# TULIAN - Simulador de Encuestas ODK

Aplicación para generar datos sintéticos realistas de encuestas de seguridad alimentaria usando contexto de desastres.

## 🚀 Inicio Rápido

```bash
# Opción 1: Script unificado (recomendado)
./start.sh

# Opción 2: Manual
source .venv/bin/activate      # Activar venv desde la raíz
cd backend && python main.py   # Backend (Puerto 9005)
cd frontend && npm run dev     # Frontend (Puerto 5505)
```

**URLs**: [Frontend](http://localhost:5505) | [API](http://localhost:9005) | [API Docs](http://localhost:9005/docs)

---

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| 📄 Parser ODK | Analiza XLSForm preservando orden y reglas |
| 🎲 Simulación | Genera datos respetando choices, constraints, relevant |
| 🌍 Contexto EM-DAT | Integra eventos de desastres reales por país |
| 📈 Progresión 4 años | Baseline vulnerable → Mejora → Sostenibilidad |
| 📊 7 Indicadores WFP | FCS, rCSI, LhCSI, HHS, FES, ECMEN, CARI |
| 📥 Export CSV | Orden exacto del ODK |

---

## 📊 Indicadores Generados

| Indicador | Fórmula |
|-----------|---------|
| **FCS** | Suma ponderada (Cereales×2, Proteína×4, etc.) |
| **rCSI** | Suma ponderada (Borrow×2, Adults×3, etc.) |
| **LhCSI** | Categorías: None/Stress/Crisis/Emergency |
| **HHS** | Hambre severa (solo Año 1 afirmativo) |
| **FES** | % gasto en alimentos |
| **ECMEN** | Capacidad económica |
| **CARI** | Clasificación consolidada |

---

## 📁 Estructura del Proyecto

```
TULIAN/
├── backend/              # API FastAPI
│   ├── main.py           # Servidor principal
│   ├── simulator.py      # Motor de simulación
│   ├── odk_parser.py     # Parser XLSForm
│   ├── context_loader.py # Cargador de datos EM-DAT
│   ├── config/           # Parámetros YAML
│   └── simulation/       # Módulos de impacto
├── frontend/             # Interfaz React + Vite
│   └── src/components/   # Componentes UI
├── scripts/              # Scripts de utilidad
│   ├── analyze/          # Scripts de análisis
│   └── run_massive_simulation.py
├── tests/                # Scripts de verificación
├── context/              # Datos EM-DAT
├── ODK/                  # Archivos XLSForm
├── MD/                   # Documentación
├── output/               # Archivos generados (ignorados en git)
└── start.sh              # Script de inicio unificado
```

---

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [Manual de Usuario](MD/manual_de_usuario.md) | Guía de uso básico |
| [Acerca de TULIAN](MD/acerca_de_tulian.md) | Descripción del proyecto |
| [Contextualización](MD/contextualizacion_de_datos.md) | Cómo funciona el contexto EM-DAT |
| [Métodos de Ejecución](MD/metodos_de_ejecucion.md) | Instrucciones detalladas |
| [Cálculos y Fórmulas](MD/calculos_y_formulas.md) | Lógica de indicadores |
| [Simulación y Contexto](MD/simulacion_y_contexto.md) | Integración de datos |

---

## 🛠️ Tecnología

**Backend**: Python 3.12, FastAPI, Pandas, Faker  
**Frontend**: React 18, Vite, TailwindCSS, Recharts, Leaflet  
**Datos**: EM-DAT (Emergency Events Database)

---

## 🔗 Repositorio

**GitHub**: [Geopoldo/simulator](https://github.com/Geopoldo/simulator)

