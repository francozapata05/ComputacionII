import aiohttp
from bs4 import BeautifulSoup
import asyncio
import time
import urllib.parse
import socket
import whois
import dns.resolver
import tldextract
import multiprocessing

# --- Global Log Queue ---
_log_queue: multiprocessing.Queue = None

def set_log_queue(queue: multiprocessing.Queue):
    """Injects the logging queue from an external module."""
    global _log_queue
    _log_queue = queue

async def get_hosting_company(session, ip):
    """Función asíncrona para obtener la empresa de hosting desde ip-api.com."""
    if not ip:
        return {"error": "No se proporcionó una dirección IP para buscar."}
    try:
        # Usamos una API pública para obtener información de la IP
        async with session.get(f"http://ip-api.com/json/{ip}") as resp:

            if resp.status != 200:
                return {"error": f"ip-api.com devolvió el estado {resp.status}"}
            
            data = await resp.json()
            
            if data.get('status') == 'success':
                return data.get('org', 'Organización no encontrada en la respuesta de ip-api.com.')
            else:
                return {"error": f"ip-api.com reportó una falla: {data.get('message')}"}
            
    except Exception as e:
        return {"error": f"Ocurrió un error al obtener la información de hosting: {e}"}
    

def _get_registrar_sync(hostname):
    print("Iniciando búsqueda de registrador para", hostname)
    """Función síncrona para obtener información del registrador usando la librería python-whois."""
    if not hostname:
        return {"error": "No se proporcionó un nombre de host."}
    try:
        w = whois.whois(hostname)
        if not w:
            return {"error": f"No se encontró información WHOIS para {hostname}."}

        # Manejamos posibles listas en los campos retornados, tomando el primer elemento
        registrar_name = w.registrar
        if isinstance(registrar_name, list):
            registrar_name = registrar_name[0] if registrar_name else None

        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0] if expiration_date else None

        registrant_name = w.name
        if isinstance(registrant_name, list):
            registrant_name = registrant_name[0] if registrant_name else None

        registrant_org = w.org
        if isinstance(registrant_org, list):
            registrant_org = registrant_org[0] if registrant_org else None

        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0] if creation_date else None

        return {
            "name": registrar_name,
            "expiration_date": str(expiration_date) if expiration_date else None,
            "registrant_name": registrant_name,
            "registrant_organization": registrant_org,
            "creation_date": str(creation_date) if creation_date else None
        }
    except Exception as e:
        return {"error": f"La búsqueda de WHOIS falló: {e}"}


def _get_nameservers_sync(hostname):
    """Función síncrona para obtener los registros NS usando dnspython."""

    if not hostname:
        return {"error": "No se proporcionó un nombre de host."}
    
    try:
        # Descomponemos en subdominio, dominio y sufijo, devuelve lista
        extracted = tldextract.extract(hostname)
        # Usamos el dominio de la lista
        domain_to_query = extracted.registered_domain

        if not domain_to_query:
            return {"error": "No se pudo determinar un dominio para consultar los registros NS."}

        answers = dns.resolver.resolve(domain_to_query, 'NS')
        nameservers = [str(rdata) for rdata in answers]
        
        return nameservers
    
    except dns.resolver.NoAnswer:
        return {"error": "No se encontraron registros NS."}
    except dns.resolver.NXDOMAIN:
        return {"error": "El dominio no existe."}
    except Exception as e:
        return {"error": f"Ocurrió un error durante la búsqueda de NS: {e}"}
    
    
def _get_mx_records_sync(hostname):
    """Función síncrona para obtener los registros MX usando dnspython."""

    if not hostname:
        return {"error": "No se proporcionó un nombre de host."}
    
    try:
        extracted = tldextract.extract(hostname)
        domain_to_query = extracted.registered_domain
        
        if not domain_to_query: 
            return {"error": "No se pudo determinar un dominio para consultar los registros MX."}
        
        answers = dns.resolver.resolve(domain_to_query, 'MX')
        mx_records = [str(rdata.exchange).rstrip('.') for rdata in answers]
        return mx_records
    
    except dns.resolver.NoAnswer:
        return {"message": f"No se encontraron registros MX para el dominio '{domain_to_query}'."}
    except dns.resolver.NXDOMAIN:
        return {"error": f"El dominio '{domain_to_query}' no existe."}
    except Exception as e:    
        return {"error": f"Ocurrió un error durante la búsqueda de MX para '{domain_to_query}': {e}"}


async def analizar_url(url):
    # Enviar log al inicio del análisis
    if _log_queue:
        try:
            _log_queue.put({
                "source": "analyzer",
                "event": "analysis_started",
                "url": url
            })
        except Exception as e:
            # Evitar que un fallo en el logging detenga el análisis
            print(f"[ERROR-LOGGING] No se pudo enviar el mensaje a la cola: {e}")

    print("Iniciando análisis para:", url)
    result = {
        "url": url,
        "status": "error",
        "title": None,
        "description": None,
        "time": None,
        "dns_info": None,
        "hosting_company": None,
        "domain_registry": None,
        "nameservers": None,
    }

    # Si la URL no comienza con http:// o https://, agregamos el prefijo
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    # Extraer el hostname de la URL
    print("Obteniendo hostname para", url)
    hostname = urllib.parse.urlparse(url).hostname

    try:
        
        # Iniciamos las búsquedas de DNS y extendidas
        print("Iniciando búsqueda de DNS para", url)
        dns_data = {}
        if hostname:
            try:
                loop = asyncio.get_running_loop()
                
                # Realizamos la búsqueda de DNS de forma asíncrona
                addr_info = await loop.getaddrinfo(hostname, None)

                ips = list(set(info[4][0] for info in addr_info))
                dns_data['ips'] = ips
            except socket.gaierror as e:
                dns_data['error'] = f"La búsqueda de DNS falló: {e}"
        else:
            dns_data['error'] = "No se pudo analizar el nombre de host desde la URL"
        result["dns_info"] = dns_data
        # --- Fin de la búsqueda de DNS ---

        # Buscamos la primer IP, contemplando posibles None
        first_ip = result.get("dns_info", {}).get("ips", [])[0] if result.get("dns_info", {}).get("ips") else None
        
        loop = asyncio.get_running_loop()

        # Realizamos las búsquedas extendidas de forma asíncrona
        async with aiohttp.ClientSession() as session:

            # Generamos asíncronamente las tareas de búsqueda de información extendida
            hosting_task = get_hosting_company(session, first_ip)
            domain_registry_task = loop.run_in_executor(None, _get_registrar_sync, hostname)
            nameservers_task = loop.run_in_executor(None, _get_nameservers_sync, hostname)
            mxservers_task = loop.run_in_executor(None, _get_mx_records_sync, hostname) # Corrected typo
            
            # Mandamos a ejecutar y esperamos a que terminen
            hosting_info, domain_registry_info, nameservers_info, mxservers_info = await asyncio.gather(
                hosting_task,
                domain_registry_task,
                nameservers_task,
                mxservers_task
            )
            # Añadimos los resultados a la respuesta
            result["hosting_company"] = hosting_info
            result["domain_registry"] = domain_registry_info
            result["nameservers"] = nameservers_info
            result["email_services"] = mxservers_info
        # --- Fin de la búsqueda de información extendida ---

        # --- Solicitud HTTP --- CONSIDERAR METER EN EL GATHER
        start = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                html = await resp.text()
                elapsed = time.time() - start

                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string.strip() if soup.title else "Sin título"
                meta = soup.find("meta", attrs={"name": "description"})

                result["status"] = "ok"
                result["title"] = title
                result["description"] = meta["content"].strip() if meta and "content" in meta.attrs else "Sin descripción"
                result["time"] = round(elapsed, 2)

    except Exception as e:
        result["error"] = str(e)

    print("Análisis completado para:", url)
    
    # Enviar log al final del análisis
    if _log_queue:
        try:
            _log_queue.put({
                "source": "analyzer",
                "event": "analysis_finished",
                "url": url,
                "status": result.get("status", "error")
            })
        except Exception as e:
            print(f"[ERROR-LOGGING] No se pudo enviar el mensaje a la cola: {e}")

    return result