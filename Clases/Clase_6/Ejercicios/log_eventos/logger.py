import os

fifo_path = "/tmp/log_fifo"
log_file = "eventos.log"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

with open(fifo_path, 'r') as fifo, open(log_file, 'a') as log:
    for linea in fifo:
        print(f"Registrando: {linea.strip()}")
        log.write(linea)
