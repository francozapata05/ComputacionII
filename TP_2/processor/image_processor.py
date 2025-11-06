import io
import requests 
from urllib.parse import urljoin
from PIL import Image
import cairosvg
import os

def generar_thumbnails(base_url, image_urls, output_dir, max_thumbnails=5):
    """Encuentra, descarga, redimensiona imágenes y genera miniaturas en disco. Devuelve una lista de rutas de archivo."""
    print(f"[Procesamiento] Iniciando generación de thumbnails para: {base_url}")
    thumbnails_paths = []
    
    # Asegurarse de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)

    # Filtrar URLs vacías o inválidas y limitar la cantidad
    valid_image_urls = [url for url in image_urls if url]
    
    for i, img_url in enumerate(valid_image_urls[:max_thumbnails]):
        try:
            # Convertir URLs relativas en absolutas (ej: /img/logo.png -> http://dominio.com/img/logo.png)
            absolute_img_url = urljoin(base_url, img_url)
            
            # Descargar la imagen
            response = requests.get(absolute_img_url, stream=True, timeout=10)
            response.raise_for_status() # Lanza un error si la petición falla

            image_bytes = response.content
            content_type = response.headers.get('Content-Type', '')

            # Si es SVG, convertir a PNG
            if 'svg' in content_type or absolute_img_url.lower().endswith('.svg'):
                print(f"  - Convirtiendo SVG a PNG para: {absolute_img_url}")
                image_bytes = cairosvg.svg2png(bytestring=image_bytes)
            
            # Leer la imagen en memoria
            image_data = io.BytesIO(image_bytes)
            with Image.open(image_data) as img:
                # Crear thumbnail (mantiene el aspect ratio, tamaño máximo 128x128)
                img.thumbnail((128, 128))
                
                # Guardar el thumbnail en un buffer en memoria en formato PNG
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                # Guardar el thumbnail en disco
                thumbnail_filename = os.path.join(output_dir, f"thumbnail_{i}.png")
                with open(thumbnail_filename, "wb") as f:
                    f.write(buffer.getvalue())
                
                thumbnails_paths.append(thumbnail_filename)
                print(f"  - Thumbnail guardado en: {thumbnail_filename}")

        except requests.exceptions.RequestException as e:
            print(f"  - Error al descargar {img_url}: {e}")
        except Exception as e:
            print(f"  - Error al procesar {img_url}: {e}")
            
    print(f"[Procesamiento] Generación de thumbnails completada. {len(thumbnails_paths)} thumbnails creados.")
    return thumbnails_paths
