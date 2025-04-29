import os

fifo_path = "/tmp/mi_fifo"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

print("Esperando mensajes...")
with open(fifo_path, 'r') as fifo:
    for linea in fifo:
        print(f"Recibido: {linea.strip()}")
