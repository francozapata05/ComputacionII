import os
import time

fifo_path = "/tmp/mi_fifo"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

with open(fifo_path, 'w') as fifo:
    for i in range(6):
        fifo.write(f"Mensaje {i+1}\n")
        fifo.flush()
        time.sleep(1)
