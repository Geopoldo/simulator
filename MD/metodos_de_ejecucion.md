# Métodos de Ejecución del Aplicativo TULIAN

Este documento describe los pasos necesarios para ejecutar tanto el Backend como el Frontend del aplicativo.

## 1. Backend (API en Python/FastAPI)

El backend maneja la lógica de procesamiento de archivos ODK, simulación y gestión de contexto.

### Requisitos Previos
- Python 3.8 o superior
- Un entorno virtual activo (recomendado)

### Instalación de Dependencias
Si no tienes las dependencias instaladas, asegúrate de activar tu entorno virtual (`venv` o `.venv`) e instalar las librerías necesarias:

```bash
# Estando en la raíz del proyecto
pip install fastapi uvicorn pandas openpyxl python-multipart pydantic
```

### Ejecución
Para iniciar el servidor de desarrollo:

1.  Activa el entorno virtual (asegúrate de estar en la raíz del proyecto):
    ```bash
    # En Linux/Mac
    source .venv/bin/activate
    # O si tu carpeta se llama venv:
    # source venv/bin/activate
    
    # En Windows
    # .venv\Scripts\activate
    ```

2.  Navega a la carpeta `backend`:
    ```bash
    cd backend
    ```

3.  Ejecuta el servidor usando Python (configurado en `main.py`):
    ```bash
    python main.py
    ```
    
    O alternativamente con Uvicorn directamente (para recarga automática):
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 9005
    ```

El servidor estará disponible en: [http://localhost:9005](http://localhost:9005)
La documentación interactiva de la API está en: [http://localhost:9005/docs](http://localhost:9005/docs)

---

## 2. Frontend (React + Vite)

El frontend es la interfaz de usuario construida con React, Vite y TailwindCSS.

### Requisitos Previos
- Node.js (versión LTS recomendada)
- npm (gestor de paquetes)

### Instalación de Dependencias
Antes de la primera ejecución, instala las librerías de Node:

1.  Navega a la carpeta `frontend`:
    ```bash
    cd frontend
    ```

2.  Instala las dependencias:
    ```bash
    npm install
    ```

### Ejecución
Para iniciar el servidor de desarrollo del frontend:

```bash
# Estando en la carpeta frontend
npm run dev
```

El aplicativo estará disponible generalmente en: [http://localhost:5505](http://localhost:5505) (o el puerto que indique la consola).

---

## 3. Ejecución Unificada (Recomendado)

Para facilitar el desarrollo, se ha incluido un script `start.sh` en la raíz del proyecto que levanta ambos servicios con un solo comando.

1.  Asegúrate de estar en la raíz del proyecto.
2.  Ejecuta:
    ```bash
    ./start.sh
    ```

Este comando activará el entorno virtual (si existe en `.venv` o `venv`), iniciará el backend y el frontend, y cerrará ambos cuando presiones `Ctrl+C`.

---

## Resumen de Comandos

| Componente | Carpeta | Comando de Inicio | URL Por Defecto |
|------------|---------|-------------------|-----------------|
| **Todo (Unificado)** | `.` | `./start.sh` | N/A |
| **Backend** | `backend/` | `python main.py` | `http://localhost:9005` |
| **Frontend** | `frontend/` | `npm run dev` | `http://localhost:5505` |
