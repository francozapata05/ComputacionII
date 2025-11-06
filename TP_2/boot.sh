#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Script de Arranque ---
# Este script inicia el servidor de procesamiento y el servidor de scraping en segundo plano.
# Asegúrate de haber ejecutado install.sh primero.

# Argumentos por defecto para server_processing.py
PROCESSING_IP="localhost"
PROCESSING_PORT="9999"
PROCESSING_PROCESSES=$(python3 -c "import multiprocessing; print(multiprocessing.cpu_count())")

# Argumentos por defecto para server_scraping.py
SCRAPING_IP="0.0.0.0"
SCRAPING_PORT="8000"
SCRAPING_WORKERS="32"
SCRAPING_MAX_HTML_SIZE="10485760" # 10 MB

echo "Iniciando el servidor de procesamiento en segundo plano..."
venv/bin/python server_processing.py -i "$PROCESSING_IP" -p "$PROCESSING_PORT" -n "$PROCESSING_PROCESSES" > /dev/null 2>&1 &
PROCESSING_PID=$!
echo "Servidor de procesamiento iniciado con PID: $PROCESSING_PID"

sleep 3 # Dar tiempo al servidor de procesamiento para iniciar

echo "Iniciando el servidor de scraping en segundo plano..."
venv/bin/python server_scraping.py -i "$SCRAPING_IP" -p "$SCRAPING_PORT" -w "$SCRAPING_WORKERS" --max-html-size "$SCRAPING_MAX_HTML_SIZE" > /dev/null 2>&1 &
SCRAPING_PID=$!
echo "Servidor de scraping iniciado con PID: $SCRAPING_PID"

echo ""
echo "Ambos servidores están corriendo en segundo plano."
echo "Para detenerlos, puedes usar 'kill $PROCESSING_PID $SCRAPING_PID'."
echo "También puedes usar 'fg' para traer un proceso al primer plano y luego Ctrl+C."
echo "O 'pkill -f python' (con precaución, detendrá todos los procesos Python)."

# Opcional: Mantener el script en ejecución para que los PIDs no se pierdan si el usuario cierra la terminal
# wait $PROCESSING_PID $SCRAPING_PID
