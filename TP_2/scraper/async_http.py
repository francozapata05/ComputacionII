import time
import aiohttp

async def fetch_url(session, url, max_html_size):
    """Usa aiohttp para descargar el contenido de una URL de forma asíncrona, con límite de tamaño manual."""
    inicio = time.time()
    try:
        async with session.get(url, timeout=30) as response:
            response.raise_for_status() # Lanza una excepción para códigos de estado HTTP 4xx/5xx

            content_length = 0
            content_chunks = []
            async for chunk in response.content.iter_chunked(4096): # Leer en trozos de 4KB
                content_length += len(chunk)
                if content_length > max_html_size:
                    raise aiohttp.ClientPayloadError(
                        f"El contenido HTML excede el tamaño máximo permitido ({max_html_size} bytes)."
                    )
                content_chunks.append(chunk)
            
            content = b"".join(content_chunks)
            duracion = time.time() - inicio
            return {
                "content": content,
                "status": response.status,
                "url": url,
                "duracion": duracion,
                "exito": True
            }
    except aiohttp.ClientPayloadError as e:
        return {
            "url": url,
            "error": str(e),
            "exito": False,
            "duracion": time.time() - inicio
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "exito": False,
            "duracion": time.time() - inicio
        }
