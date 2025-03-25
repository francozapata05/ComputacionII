import os
import time

pid = os.fork()

if pid == 0:  # Código del proceso hijo
    print(f"Hijo ({os.getpid()}) terminando...")
    exit(0)  # El hijo finaliza
else:
    print(f"Padre ({os.getpid()}) esperando...")  
    time.sleep(10)  # El padre no llama a wait(), creando un zombi
