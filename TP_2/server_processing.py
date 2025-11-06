import socketserver
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime
from urllib.parse import urlparse
import concurrent.futures
import multiprocessing

# --- Funciones de Procesamiento (Implementación Real) ---

from processor.screenshot import generar_screenshot
from processor.performance import analizar_rendimiento
from processor.image_processor import generar_thumbnails

def _process_single_url_task(url, image_urls, output_dir):
    """Función que ejecuta todas las tareas de procesamiento para una URL en un proceso del pool."""
    driver = None
    try:
        # 1. Iniciar el navegador una sola vez por tarea
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Navegar a la URL
        driver.get(url)

        # 2. Ejecutar las tareas de procesamiento
        screenshot_path = generar_screenshot(driver, output_dir)
        performance_data = analizar_rendimiento(driver)
        thumbnails_paths = generar_thumbnails(url, image_urls, output_dir)

        return {
            "screenshot": screenshot_path,
            "performance": performance_data,
            "thumbnails": thumbnails_paths
        }
    except Exception as e:
        print(f"[Procesamiento - Pool] Error en la tarea para {url}: {e}")
        return {"error": str(e)}
    finally:
        if driver:
            driver.quit()


# --- Lógica del Servidor TCP ---

from common.protocol import recibir_mensaje_completo, enviar_mensaje_completo

class MyTCPHandler(socketserver.BaseRequestHandler):
    # El pool de procesos se asignará a esta variable de clase
    executor = None

    def handle(self):
        print(f"Conexión entrante de {self.client_address[0]}")
        
        respuesta = {}

        try:
            data_recibida = recibir_mensaje_completo(self.request)
            if data_recibida is None:
                print("El cliente cerró la conexión inesperadamente.")
                return

            info_scraping = json.loads(data_recibida.decode('utf-8'))
            url = info_scraping.get("url")
            print(f"Recibida solicitud de procesamiento para: {url}")

            # Generar nombre de carpeta único
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            parsed_url = urlparse(url)
            sanitized_host = parsed_url.netloc.replace(".", "_").replace(":", "_")
            output_folder_name = f"{timestamp}-{sanitized_host}"
            base_output_dir = "requests"
            output_dir = os.path.join(base_output_dir, output_folder_name)
            
            os.makedirs(output_dir, exist_ok=True)

            # Enviar la tarea al pool de procesos y esperar el resultado
            future = self.executor.submit(_process_single_url_task, url, info_scraping.get("image_urls", []), output_dir)
            processing_result = future.result() # Bloquea hasta que la tarea del pool termine

            if "error" in processing_result:
                respuesta = {"url": url, "status": "error", "error": processing_result["error"]}
            else:
                respuesta = {
                    "url": url,
                    "status": "success",
                    "processing_data": processing_result
                }

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error procesando la solicitud: {e}")
            respuesta = {"status": "error", "error": f"Datos inválidos recibidos: {e}"}
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            respuesta = {"status": "error", "error": str(e)}
        finally:
            # 6. Enviar la respuesta de vuelta al scraper (si se ha construido)
            if respuesta:
                enviar_mensaje_completo(self.request, respuesta)
                print(f"Respuesta enviada para: {respuesta.get('url', 'URL desconocida')}")


import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de Procesamiento Distribuido")
    parser.add_argument("-i", "--ip", type=str, default="localhost",
                        help="Dirección de escucha")
    parser.add_argument("-p", "--port", type=int, default=9999,
                        help="Puerto de escucha")
    parser.add_argument("-n", "--processes", type=int, default=multiprocessing.cpu_count(),
                        help="Número de procesos en el pool (default: CPU count)")
    
    args = parser.parse_args()

    HOST, PORT = args.ip, args.port

    # Inicializar el ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.processes) as executor:
        MyTCPHandler.executor = executor # Asignar el executor a la clase del handler

        # Usar ThreadingTCPServer para manejar las conexiones y pasar el trabajo al pool de procesos
        # ThreadingTCPServer es adecuado aquí porque el trabajo pesado se descarga al ProcessPoolExecutor
        server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
        server.allow_reuse_address = True

        print(f"Servidor de procesamiento escuchando en {HOST}:{PORT} con {args.processes} procesos worker.")
        print("Presiona Ctrl-C para detener.")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Servidor detenido por el usuario.")
        finally:
            server.shutdown()
            executor.shutdown(wait=True)