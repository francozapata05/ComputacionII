import os

fifo_path = "/tmp/mi_fifo"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

with open(fifo_path, 'r') as fifo:
    while True:
        linea = fifo.readline()
        if not linea:
            break
        print(f"PID {os.getpid()} leyó: {linea.strip()}")
