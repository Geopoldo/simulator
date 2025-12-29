# TULIAN - Simulador de Encuestas ODK

Aplicación para generar datos sintéticos realistas de encuestas de seguridad alimentaria usando contexto de desastres.

## 🚀 Inicio Rápido

```bash
# Backend (Puerto 9005)
cd backend && source venv/bin/activate && python main.py

# Frontend (Puerto 5505)
cd frontend && npm run dev
```

**URLs**: [Frontend](http://localhost:5505) | [API](http://localhost:9005)

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

## 📁 Estructura

```
TULIAN/
├── backend/
│   ├── main.py          # API FastAPI
│   ├── simulator.py     # Motor de simulación
│   ├── odk_parser.py    # Parser XLSForm
│   ├── rules.py         # Evaluador relevant/constraint
│   ├── profiles.py      # Perfiles por país
│   └── config/          # Parámetros YAML
├── frontend/src/
│   ├── App.jsx          # Aplicación principal
│   └── components/      # Componentes React
├── context/             # Datos EM-DAT
├── ODK/                 # Archivos XLSForm
└── MD/                  # Documentación
```

---

## 📖 Documentación

- [Manual de Usuario](MD/manual_de_usuario.md)
- [Acerca de TULIAN](MD/acerca_de_tulian.md)
- [Checklist de Requisitos](MD/checklist_requisitos.md)
- [Simulación y Contexto](MD/simulacion_y_contexto.md)

---

## 🛠️ Tecnología

**Backend**: Python 3.12, FastAPI, Pandas, Faker
**Frontend**: React 18, Vite, TailwindCSS, Recharts, Leaflet
