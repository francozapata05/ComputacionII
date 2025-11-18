import socketserver
import json
import uuid
import asyncio
import threading
from concurrent.futures import Future
from analyzer_async import analizar_url
import socket

# Diccionario para tareas en segundo plano
pending_tasks = {}
task_lock = threading.Lock()

class AsyncioEventLoop(threading.Thread):
    """
    Clase que encapsula un bucle de eventos asyncio que corre en un hilo separado.
    Permite enviar corutinas a ejecutar desde otros hilos de forma segura.
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = None
        self.ready = threading.Event()

    def run(self):
        """
        Este método se ejecuta en el nuevo hilo.
        Configura y corre el bucle de eventos asyncio.
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.ready.set()  # Señaliza que el bucle está listo
        self.loop.run_forever()

    def submit(self, coroutine) -> Future:
        """
        Envía una corutina al bucle de eventos para ser ejecutada.
        Retorna un `concurrent.futures.Future` que puede ser usado para
        obtener el resultado de la corutina.
        """
        if not self.ready.is_set():
            self.ready.wait() # Espera a que el bucle esté listo
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def stop(self):
        """
        Detiene el bucle de eventos y espera a que el hilo termine.
        """
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(4096).decode()
            if not data:
                return
            
            # Determinar la familia de la conexión para fines de logging/debugging
            if len(self.client_address) == 4:
                protocolo = "IPv6"
            elif len(self.client_address) == 2:
                protocolo = "IPv4"
            else:
                protocolo = "Desconocido"
            
            # print(f"[{protocolo}] Conexión de: {self.client_address} en hilo {threading.current_thread().name}")

            request_data = json.loads(data)
            action = request_data.get("action")

            # Obtenemos el loop de asyncio del servidor
            asyncio_loop = self.server.asyncio_loop

            if action == "analizar":
                url = request_data.get("url")
                if not url:
                    self._responder({"error": "Falta parámetro 'url'"})
                    return

                task_id = str(uuid.uuid4())

                # Creamos la corutina y la enviamos al bucle de asyncio
                coroutine = analizar_url(url)
                future = asyncio_loop.submit(coroutine)

                with task_lock:
                    pending_tasks[task_id] = future

                self._responder({
                    "status": "enqueued",
                    "task_id": task_id
                })

            elif action == "consultar":
                task_id = request_data.get("task_id")
                if not task_id:
                    self._responder({"error": "Falta 'task_id'"})
                    return

                with task_lock:
                    task = pending_tasks.get(task_id)

                if not task:
                    self._responder({"error": "Tarea no encontrada"})
                elif not task.done():
                    self._responder({"status": "pending"})
                else:
                    try:
                        # Obtenemos el resultado del future
                        result = task.result()
                        self._responder({
                            "status": "done",
                            "task_id": task_id,
                            "result": result
                        })
                    except Exception as e:
                        self._responder({
                            "status": "error",
                            "task_id": task_id,
                            "error": f"Error en la tarea: {str(e)}"
                        })
                    finally:
                        # Opcional: eliminar la tarea una vez consultada
                        with task_lock:
                            if task_id in pending_tasks:
                                del pending_tasks[task_id]

            else:
                self._responder({"error": "Acción desconocida"})

        except json.JSONDecodeError:
            self._responder({"error": "Request malformado, debe ser JSON."})
        except Exception as e:
            self._responder({"error": str(e)})

    def _responder(self, mensaje):
        self.request.sendall(json.dumps(mensaje).encode())

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Clase base para el servidor, sin address_family predefinido."""
    allow_reuse_address = True
    
# Clases específicas para cada protocolo
class IPv4ThreadedTCPServer(ThreadedTCPServer):
    address_family = socket.AF_INET
    
class IPv6ThreadedTCPServer(ThreadedTCPServer):
    address_family = socket.AF_INET6
    
    def server_bind(self):
        """Asegura que el socket IPv6 solo escuche en IPv6."""
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        super().server_bind()

# --- Función para iniciar el servidor en un hilo separado ---

def iniciar_servidor_tcp(server_class, host, port, handler, asyncio_loop):
    """Inicia una instancia de servidor TCP en un hilo separado."""
    
    server_type = "IPv4" if server_class.address_family == socket.AF_INET else "IPv6"
    
    try:
        server = server_class((host, port), handler)
        server.asyncio_loop = asyncio_loop # Adjuntamos el loop al servidor
        
        print(f"Iniciando servidor {server_type} en {host}:{port}")
        
        # El servidor se ejecuta en un hilo Daemon para que termine con el proceso principal
        thread = threading.Thread(
            target=server.serve_forever, 
            daemon=True,
            name=f"ServerThread-{server_type}"
        )
        thread.start()
        return server, thread
    except Exception as e:
        print(f"ERROR al iniciar servidor {server_type} en {host}:{port}: {e}")
        return None, None

# --- Main execution ---
if __name__ == "__main__":
    PORT = 9999
    
    print("Iniciando bucle de eventos de asyncio en segundo plano...")
    asyncio_loop = AsyncioEventLoop()
    asyncio_loop.start()

    servidores = []

    # 1. Obtener direcciones disponibles usando AF_UNSPEC y getaddrinfo
    # Usamos None para el host para obtener todas las interfaces disponibles
    direcciones = socket.getaddrinfo(
        None, 
        PORT, 
        socket.AF_UNSPEC, 
        socket.SOCK_STREAM, 
        socket.IPPROTO_TCP, 
        socket.AI_PASSIVE # Importante para sockets de servidor
    )
    
    # 2. Iniciar un servidor por cada familia de direcciones única
    familias_iniciadas = set()
    for addr_info in direcciones:
        familia, tipo_socket, protocolo, canonname, sa = addr_info
        host, port = sa[:2] # Tomamos la dirección y puerto
        
        if familia == socket.AF_INET and familia not in familias_iniciadas:
            # Servidor IPv4
            server_class = IPv4ThreadedTCPServer
            srv, thread = iniciar_servidor_tcp(
                server_class, host, PORT, ThreadedTCPRequestHandler, asyncio_loop
            )
            if srv:
                servidores.append(srv)
                familias_iniciadas.add(familia)
                
        elif familia == socket.AF_INET6 and familia not in familias_iniciadas:
            # Servidor IPv6
            server_class = IPv6ThreadedTCPServer
            srv, thread = iniciar_servidor_tcp(
                server_class, host, PORT, ThreadedTCPRequestHandler, asyncio_loop
            )
            if srv:
                servidores.append(srv)
                familias_iniciadas.add(familia)
                
    if not servidores:
        print("No se pudo iniciar ningún servidor. Verifique las interfaces de red.")
        asyncio_loop.stop()
        exit(1)

    print("\nServidores TCP iniciados y listos para recibir peticiones.")
    
    try:
        # Mantenemos el hilo principal vivo, sin necesidad de otro loop
        while True:
            threading.Event().wait(1) # Espera pasiva
            
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        for srv in servidores:
            srv.shutdown()
        
    finally:
        print("Deteniendo bucle de asyncio...")
        asyncio_loop.stop()
        print("Servidores y bucle de asyncio cerrados.")
