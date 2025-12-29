# TULIAN Codebase Documentation

> **Last Updated:** 2025-12-29  
> **Purpose:** Track code complexity and identify refactoring opportunities

---

## 📊 Summary Metrics

| Category | Files | Total Lines |
|----------|-------|-------------|
| Backend (Python) | 8 | 3,095 |
| Frontend (JSX) | 9 | 1,336 |
| Config (YAML) | 2 | 209 |
| **Total** | **19** | **4,640** |

---

## 🚨 Complexity Thresholds

| Lines | Status | Action |
|-------|--------|--------|
| < 200 | 🟢 Good | Maintain |
| 200-500 | 🟡 Monitor | Consider splitting |
| 500-800 | 🟠 Refactor Soon | Plan modularization |
| > 800 | 🔴 Critical | Immediate action |

---

## 🐍 Backend Files (Python)

### Critical (> 800 lines)
| File | Lines | Functions | Status | Notes |
|------|-------|-----------|--------|-------|
| `profiles.py` | 332 | ~12 | 🟢 Good | Country data moved to country_profiles.yaml |
| `simulator.py` | 1,144 | ~28 | 🟡 Monitor | Core engine. Duplicates removed, uses simulation/ |

### Monitor (200-500 lines)
| File | Lines | Functions | Status | Notes |
|------|-------|-----------|--------|-------|
| `config_loader.py` | 232 | 15 | 🟢 Good | Config API - well-structured |
| `simulation/disaster_impact.py` | 203 | 5 | 🟢 Good | **NEW** - Extracted from simulator |

### Good (< 200 lines)
| File | Lines | Functions | Status | Notes |
|------|-------|-----------|--------|-------|
| `main.py` | 162 | 8 | 🟢 Good | FastAPI routes |
| `verify_context_impact.py` | 160 | 5 | 🟢 Good | Test script |
| `context_loader.py` | 132 | 4 | 🟢 Good | EM-DAT loader |
| `odk_parser.py` | 106 | 6 | 🟢 Good | ODK Excel parser |
| `simulation/humanitarian.py` | 88 | 4 | 🟢 Good | **NEW** - Extracted |
| `rules.py` | 43 | 2 | 🟢 Good | Relevance/constraint logic |
| `simulation/__init__.py` | 34 | 0 | 🟢 Good | Package exports |

---

## ⚛️ Frontend Files (JSX)

### Monitor (200-500 lines)
| File | Lines | Components | Status | Notes |
|------|-------|------------|--------|-------|
| `SceneSimulation.jsx` | 232 | 1 | 🟡 Monitor | Simulation controls |
| `SceneVisualization.jsx` | 213 | 1 | 🟡 Monitor | Dashboard orchestrator |
| `SceneUpload.jsx` | 205 | 1 | 🟡 Monitor | File upload |

### Good (< 200 lines)
| File | Lines | Components | Status | Notes |
|------|-------|------------|--------|-------|
| `DashboardInsights.jsx` | 183 | 1 | 🟢 Good | AI insights panel |
| `DashboardCharts.jsx` | 179 | 1 | 🟢 Good | Trend charts |
| `CountryMapSelector.jsx` | 130 | 1 | 🟢 Good | Map selector |
| `DashboardMap.jsx` | 98 | 1 | 🟢 Good | Geographic view |
| `App.jsx` | 86 | 1 | 🟢 Good | Root component |
| `main.jsx` | 10 | 0 | 🟢 Good | Entry point |

---

## 📁 Configuration Files (YAML)

| File | Lines | Purpose |
|------|-------|---------|
| `simulation_params.yaml` | 139 | Disaster thresholds, progression curve |
| `field_mappings.yaml` | 70 | FCS/RCSI/HHS field definitions |
| `country_profiles.yaml` | 936 | Country and region data (72 countries) |

---

## 🔧 Recommended Refactoring Actions

### Priority 1: `profiles.py` (1,256 lines)
**Problem:** Contains hardcoded country profile definitions  
**Solution:** 
- Extract regional defaults to `config/regional_defaults.yaml`
- Keep only `CountryProfile` class and `build_country_profile()`
- Target: < 200 lines

### Priority 2: `simulator.py` (1,004 lines)
**Problem:** Monolithic simulation engine  
**Solution:** Split into modules:
```
simulation/
  __init__.py
  core.py            # Main Simulator class
  disaster_impact.py # Impact calculations
  field_generators.py # FCS/expense generation
  progression.py     # Recovery logic
```
**Target:** Each module < 200 lines

### Priority 3: Frontend Scenes (200+ lines each)
**Problem:** Scene components doing too much  
**Solution:** 
- Extract reusable UI components
- Move business logic to custom hooks

---

## 📈 Code Growth Tracking

| Date | Backend | Frontend | Config | Total | Notes |
|------|---------|----------|--------|-------|-------|
| 2025-12-16 | 3,095 | 1,336 | 209 | 4,640 | Initial baseline after config externalization |
| 2025-12-29 | 3,512 | 1,336 | 209 | 5,057 | simulator.py grew +417 lines despite module extraction |
| 2025-12-29 | 3,235 | 1,350 | 209 | 4,794 | Removed 277 dup lines from simulator.py |
| 2025-12-29 | 2,310 | 1,350 | 1,145 | 4,805 | profiles.py -925 lines → YAML |

---

## 🎯 Target Architecture

```
TULIAN/
├── backend/
│   ├── config/           # ✅ Created
│   │   ├── simulation_params.yaml
│   │   ├── field_mappings.yaml
│   │   └── regional_defaults.yaml  # TODO
│   ├── simulation/       # TODO: Split simulator.py
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── disaster_impact.py
│   │   └── field_generators.py
│   ├── config_loader.py  # ✅ Created
│   ├── context_loader.py # ✅ Good
│   ├── main.py           # ✅ Good
│   ├── odk_parser.py     # ✅ Good
│   └── rules.py          # ✅ Good
└── frontend/
    └── src/
        ├── components/   # ✅ Good structure
        ├── hooks/        # TODO: Extract logic
        └── utils/        # TODO: Add utilities
```
