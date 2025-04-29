import os
import time
import random

fifo_path = "/tmp/log_fifo"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

mensajes = ["Inicio del sistema", "Usuario conectado", "Error: archivo no encontrado", "Proceso finalizado"]

with open(fifo_path, 'w') as fifo:
    for _ in range(5):
        mensaje = random.choice(mensajes)
        fifo.write(mensaje + '\n')
        fifo.flush()
        print(f"Evento enviado: {mensaje}")
        time.sleep(1)
