#!/bin/bash

# Función para matar los procesos hijos al salir
cleanup() {
    echo "Deteniendo servicios..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Ejecutar cleanup cuando reciba SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "Iniciando TULIAN..."

# 1. Iniciar Backend
echo "Levantando Backend..."
cd backend

# Activar el entorno virtual del backend
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "ADVERTENCIA: No se encontró entorno virtual en backend. Intentando con python del sistema."
fi

python main.py &
BACKEND_PID=$!
cd ..

# 2. Iniciar Frontend
echo "Levantando Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Presiona Ctrl+C para detener ambos servicios."

# Esperar a que cualquier proceso termine
wait -n

# Si uno termina, matar al otro y salir
cleanup
