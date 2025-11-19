import multiprocessing
import time
import json
from datetime import datetime

LOG_FILE = "analysis.log"
END = None # Mensaje especial para terminar el proceso

def logger_process(queue: multiprocessing.Queue):
    """
    Este proceso se ejecuta en segundo plano.
    Espera mensajes en la cola y los escribe en un archivo de log.
    """
    print(f"Proceso de logging iniciado. Escribiendo en '{LOG_FILE}'.")
    try:
        with open(LOG_FILE, "a") as f:
            while True:
                # Espera bloqueante hasta que haya un mensaje en la cola
                message = queue.get()

                # Si recibimos el "poison pill", terminamos el bucle
                if message == END:
                    print("Proceso de logging recibio señal para terminar. Cerrando...")
                    break
                
                # Construimos el registro de log
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    **message # Combina el timestamp con el mensaje recibido
                }

                # Escribimos la entrada como una línea JSON en el archivo
                f.write(json.dumps(log_entry) + "\n")
                f.flush() # Asegura que se escriba inmediatamente en el disco

    except Exception as e:
        # Si algo sale mal, lo imprimimos en la consola del servidor
        print(f"[ERROR EN PROCESO DE LOGGING]: {e}")

