import socketserver
import json
import uuid
import asyncio
import threading
from concurrent.futures import Future
from analyzer_async import analizar_url

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
                    # Obtenemos el resultado del future
                    result = task.result()
                    self._responder({
                        "status": "done",
                        "task_id": task_id,
                        "result": result
                    })
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
    allow_reuse_address = True


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    print("Iniciando bucle de eventos de asyncio en segundo plano...")
    asyncio_loop = AsyncioEventLoop()
    asyncio_loop.start()

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.asyncio_loop = asyncio_loop # Adjuntamos el loop al servidor

    try:
        print(f"Servidor TCP escuchando en {HOST}:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Cerrando servidor...")
    finally:
        server.shutdown()
        server.server_close()
        print("Deteniendo bucle de asyncio...")
        asyncio_loop.stop()
        print("Servidor cerrado.")