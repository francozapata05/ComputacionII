import os
import time

fifo_path = "/tmp/mi_fifo"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

with open(fifo_path, 'w') as fifo:
    for i in range(3):
        mensaje = f"Mensaje {i+1}\n"
        print(f"Enviando: {mensaje.strip()}")
        fifo.write(mensaje)
        fifo.flush()
        time.sleep(1)
