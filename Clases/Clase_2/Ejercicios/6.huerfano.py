import os
import time

pid = os.fork()

if pid > 0:
    print(f"Padre ({os.getpid()}) terminando...")
    exit(0)  # Padre termina
else:
    time.sleep(5)  # Hijo sigue ejecutándose
    print(f"Hijo ({os.getpid()}) ahora es huérfano, adoptado por init (PID {os.getppid()})")
