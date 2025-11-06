import asyncio
import time
import aiohttp
from flask import Flask, json, jsonify, request
from common.async_protocol import async_recibir_mensaje_completo, async_enviar_mensaje_completo
from scraper.async_http import fetch_url
from scraper.html_parser import parse_html_content
from scraper.metadata_extractor import extract_meta_tags

# --- Funciones de Comunicación ---

async def comunicar_con_procesamiento(datos_scraping, max_retries=3, retry_delay=1):
    """Se conecta al servidor de procesamiento, envía datos y recibe resultados de forma asíncrona, con reintentos."""
    HOST, PORT = "localhost", 9999
    
    for attempt in range(max_retries):
        reader = None
        writer = None
        try:
            reader, writer = await asyncio.open_connection(HOST, PORT)
            
            # Enviar datos al servidor de procesamiento
            await async_enviar_mensaje_completo(writer, datos_scraping)
            
            # Recibir respuesta
            respuesta_raw = await async_recibir_mensaje_completo(reader)
            if respuesta_raw:
                return json.loads(respuesta_raw.decode('utf-8'))
            else:
                return {"status": "error", "error": "No se recibió respuesta del servidor de procesamiento"}
        except ConnectionRefusedError:
            print(f"[Comunicación] Intento {attempt + 1}/{max_retries}: Conexión rechazada. Reintentando en {retry_delay}s...")
            await asyncio.sleep(retry_delay)
        except Exception as e:
            print(f"[Comunicación] Intento {attempt + 1}/{max_retries}: Error de comunicación asíncrona: {e}. Reintentando en {retry_delay}s...")
            await asyncio.sleep(retry_delay)
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
    
    return {"status": "error", "error": f"Fallo la comunicación con el servidor de procesamiento después de {max_retries} intentos."}

# --- Funciones de Scraping y Procesamiento ---

from urllib.parse import urlparse

async def extraer_y_procesar_informacion(session, url, max_html_size, global_semaphore, domain_semaphores):
    """
    Orquesta el proceso completo para una URL:
    1. Descarga el contenido.
    2. Extrae la información de scraping.
    3. Se comunica con el servidor de procesamiento.
    4. Compone la respuesta final.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Obtener o crear el semáforo para este dominio, no pueden haber 30 consultas simultaneas, nos pueden banear
    if domain not in domain_semaphores:
        domain_semaphores[domain] = asyncio.Semaphore(5) # Límite de 5 conexiones por dominio
    domain_semaphore = domain_semaphores[domain]

    async with global_semaphore:
        async with domain_semaphore:
            fetch_result = await fetch_url(session, url, max_html_size)

    if not fetch_result["exito"]:
        return fetch_result

    # 1. Extraer datos con BeautifulSoup
    html_content = fetch_result["content"]
    
    parsed_data = parse_html_content(html_content)
    meta_tags_filtradas = extract_meta_tags(html_content)

    titulo = parsed_data["titulo"]
    enlaces = parsed_data["enlaces"]
    cantidad_de_imagenes = parsed_data["cantidad_de_imagenes"]
    image_urls = parsed_data["image_urls"]
    estructura_conteo = parsed_data["estructura_conteo"]

    # 2. Comunicarse con el servidor de procesamiento
    datos_para_procesamiento = {
        "url": url,
        "image_urls": image_urls
    }
    processing_result = await comunicar_con_procesamiento(datos_para_procesamiento)

    # 3. Componer la respuesta final
    respuesta_final = {
        "url": url,
        "timestamp": time.time(),
        "status": processing_result.get("status", "error"),
        "scraping_data": {
            "title": titulo,
            "links": enlaces,
            "meta_tags": meta_tags_filtradas,
            "structure": estructura_conteo,
            "images_count": cantidad_de_imagenes
        },
        "processing_data": {
            "screenshot": processing_result.get("processing_data", {}).get("screenshot"),
            "performance": processing_result.get("processing_data", {}).get("performance"),
            "thumbnails": processing_result.get("processing_data", {}).get("thumbnails")
        }
    }
    
    if processing_result.get("status") != "success":
        respuesta_final["error"] = processing_result.get("error", "Error desconocido en el servidor de procesamiento")

    return respuesta_final

async def scraper_concurrente_async(urls, max_html_size, max_concurrent_workers):
    """Maneja múltiples URLs de forma concurrente usando aiohttp y asyncio."""
    inicio = time.time()
    async with aiohttp.ClientSession() as session:
        global_semaphore = asyncio.Semaphore(max_concurrent_workers)
        domain_semaphores = {}
        tasks = [extraer_y_procesar_informacion(session, url, max_html_size, global_semaphore, domain_semaphores) for url in urls]
        resultados = await asyncio.gather(*tasks, return_exceptions=True)
    
    tiempo_total = time.time() - inicio
    return resultados, tiempo_total

# --- Servidor Flask ---

app = Flask(__name__)

@app.route("/scrape", methods=['POST'])
def handle_scrape():
    """Endpoint de Flask para recibir las URLs y disparar el scraping."""
    data = request.get_json()
    if not data or "urls" not in data:
        return jsonify({"error": "Se requiere un JSON con la clave 'urls'"}), 400

    urls = data["urls"]
    if not isinstance(urls, list):
        return jsonify({"error": "'urls' debe ser una lista"}), 400

    # Ejecutar el scraper asíncrono desde el endpoint síncrono de Flask
    # Pasar el max_html_size obtenido de los argumentos CLI
    resultados, tiempo_total = asyncio.run(scraper_concurrente_async(urls, app.config['MAX_HTML_SIZE'], app.config['WORKERS']))
    
    # Estadísticas
    exitosos = sum(1 for r in resultados if isinstance(r, dict) and r.get("status") == "success")
    
    return jsonify({
        "resultados": resultados,
        "estadisticas": {
            "total_urls": len(urls),
            "exitosos": exitosos,
            "fallidos": len(urls) - exitosos,
            "tiempo_total_segundos": tiempo_total
        }
    })

import argparse

# --- Punto de Entrada ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de Scraping Web Asíncrono")
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0",
                        help="Dirección de escucha (soporta IPv4/IPv6)")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Puerto de escucha")
    parser.add_argument("-w", "--workers", type=int, default=32,
                        help="Número de workers para el scraper concurrente (no usado directamente por asyncio.gather)")
    parser.add_argument("--max-html-size", type=int, default=10 * 1024 * 1024, # 10 MB
                        help="Tamaño máximo del contenido HTML a descargar en bytes (default: 10MB)")
    
    args = parser.parse_args()

    # Almacenar max_html_size y workers en la configuración de la aplicación Flask
    app.config['MAX_HTML_SIZE'] = args.max_html_size
    app.config['WORKERS'] = args.workers

    app.run(host=args.ip, port=args.port)
