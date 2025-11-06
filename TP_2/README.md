# TP2 - Sistema de Scraping y Análisis Web Distribuido

## Descripción del Proyecto

Este proyecto implementa un sistema distribuido de scraping y análisis web utilizando Python. Consiste en dos servidores que trabajan de forma coordinada:

1.  **Servidor de Extracción (server_scraping.py)**: Un servidor asíncrono (asyncio + Flask) que recibe URLs a través de peticiones HTTP, realiza el scraping de la página, extrae información clave (título, enlaces, meta tags, imágenes, estructura) y se comunica con el servidor de procesamiento.
2.  **Servidor de Procesamiento (server_processing.py)**: Un servidor paralelo (multiprocessing + socketserver) que recibe solicitudes del servidor de extracción y realiza tareas computacionalmente intensivas como la captura de screenshots, análisis de rendimiento y generación de thumbnails de imágenes.

Ambos servidores se comunican mediante un protocolo de sockets binario eficiente.

## Instalación de Requerimientos

Para configurar y ejecutar el proyecto, sigue estos pasos:

1.  **Clonar el repositorio** (si aún no lo has hecho):
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd TP_2 # O el nombre de tu carpeta
    ```

2.  **Ejecutar el script de instalación**:
    Este script creará un entorno virtual (`venv/`) e instalará todas las dependencias de Python necesarias.

    ```bash
    ./install.sh
    ```

    **Nota**: Si encuentras problemas con la instalación de `cairosvg` o `Pillow` en Linux, asegúrate de tener las librerías de desarrollo de Cairo y zlib instaladas en tu sistema (ej: `sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev`).

## Ejecución de los Servidores

El proyecto incluye un script `boot.sh` para iniciar ambos servidores de forma concurrente en segundo plano.

1.  **Inicia ambos servidores**:
    ```bash
    ./boot.sh
    ```
    Este script iniciará `server_processing.py` (en `localhost:9999`) y `server_scraping.py` (en `0.0.0.0:8000`).

2.  **Para detener los servidores**:
    El script `boot.sh` te mostrará los PIDs de ambos procesos. Puedes usar `kill <PID1> <PID2>` para detenerlos. Alternativamente, puedes usar `killall python` (con precaución, ya que detendrá todos los procesos de Python) o `fg` para traer un proceso al primer plano y luego `Ctrl+C`.

## Uso del Sistema (Envío de Peticiones)

Una vez que ambos servidores estén corriendo, puedes enviar solicitudes de scraping al `server_scraping.py` utilizando `curl` o cualquier cliente HTTP.

**Ejemplo de petición:**

```bash
curl -X POST http://127.0.0.1:8000/scrape \
-H "Content-Type: application/json" \
-d '{"urls": ["https://www.python.org", "https://pypi.org", "https://www.um.edu.ar"]}'
```

**Parámetros configurables (al iniciar los servidores)**:

Puedes pasar argumentos a los servidores a través del script `boot.sh` (o ejecutándolos directamente):

*   **`server_scraping.py`**:
    ```bash
    ./boot.sh server_scraping.py -i <IP> -p <PUERTO> -w <WORKERS> --max-html-size <BYTES>
    # Ejemplo: ./boot.sh server_scraping.py -i 0.0.0.0 -p 8000 -w 10 --max-html-size 5242880
    ```
    *   `-i IP`: Dirección de escucha (ej: `0.0.0.0` para IPv4, `::` para IPv6).
    *   `-p PORT`: Puerto de escucha.
    *   `-w WORKERS`: Número de tareas de scraping concurrentes (límite de semáforo).
    *   `--max-html-size`: Tamaño máximo del contenido HTML a descargar en bytes.

*   **`server_processing.py`**:
    ```bash
    ./boot.sh server_processing.py -i <IP> -p <PUERTO> -n <PROCESOS>
    # Ejemplo: ./boot.sh server_processing.py -i localhost -p 9999 -n 4
    ```
    *   `-i IP`: Dirección de escucha.
    *   `-p PORT`: Puerto de escucha.
    *   `-n PROCESSES`: Número de procesos en el pool para tareas de procesamiento.

Si quieres configurar parámetros específicos para ambos servidores, ejecuta:

    python server_scraping.py -i <IP> -p <PUERTO> -w <WORKERS> --max-html-size <BYTES>
    python server_processing.py -i <IP> -p <PUERTO> -n <PROCESOS>
    

## Salida de Archivos

Los screenshots y thumbnails generados por el `server_processing.py` se guardarán en una carpeta llamada `requests/` en la raíz del proyecto. Dentro de `requests/`, se crearán subcarpetas con el formato `timestamp-dominio_sanitizado/` para cada URL procesada.

