#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# --- Script de Instalación ---
# Este script crea un entorno virtual y instala las dependencias.

# 1. Crear entorno virtual llamado 'venv' si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual en 'venv'..."
    python3 -m venv venv
else
    echo "El entorno virtual 'venv' ya existe."
fi

# 2. Instalar dependencias desde requirements.txt
echo "Instalando dependencias..."
venv/bin/pip install -r requirements.txt

echo "Instalación completada."
