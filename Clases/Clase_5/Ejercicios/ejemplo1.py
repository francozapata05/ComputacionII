import os
from multiprocessing import Queue
import time

# Función que simula el productor
def productor(q):
    for i in range(5):
        mensaje = f"Dato {i}"
        q.put(mensaje)
        print(f"[Productor] Enviado: {mensaje}")
        time.sleep(0.5)

# Función que simula el consumidor
def consumidor(q):
    for i in range(5):
        try:
            # Intentará obtener el dato de la cola con un tiempo de espera de 5 segundos
            dato = q.get(timeout=5)
            print(f"[Consumidor] Recibido: {dato}")
        except:
            print("[Consumidor] Error: No se recibió dato en el tiempo permitido")
        time.sleep(0.5)

if __name__ == "__main__":
    q = Queue(10)  # Crea una cola con capacidad máxima de 10 elementos
    pid = os.fork()

    if pid == 0:
        # Proceso hijo, ejecuta la función consumidor
        consumidor(q)
        os._exit(0)
    else:
        # Proceso padre, ejecuta la función productor
        productor(q)
        os.wait()
        print("[Main] Comunicación finalizada")
