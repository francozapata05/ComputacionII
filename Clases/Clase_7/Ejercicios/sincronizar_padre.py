import os
import signal
import time

# Handler que el padre usará
def handler(sig, frame):
    print(f"[PADRE] Recibí la señal {sig}. El hijo terminó.")

# Establecer el handler para SIGUSR1
signal.signal(signal.SIGUSR1, handler)

# Crear un proceso hijo
pid = os.fork()

if pid == 0:
    # --- PROCESO HIJO ---
    print("[HIJO] Trabajando...")
    time.sleep(3)
    print("[HIJO] Enviando señal al padre...")
    os.kill(os.getppid(), signal.SIGUSR1)
    print("[HIJO] Terminé.")
    os._exit(0)
else:
    # --- PROCESO PADRE ---
    print("[PADRE] Esperando señal de mi hijo...")
    signal.pause()  # Bloquea hasta que reciba una señal
    print("[PADRE] Continuo mi ejecución.")
