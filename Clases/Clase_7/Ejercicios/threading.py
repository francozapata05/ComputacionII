import signal
import threading
import os
import time

def signal_handler(signum, frame):
    print(f"\n🔔 Señal recibida en hilo principal: {signum}")

def worker():
    print("🧵 Hilo secundario trabajando...")
    while True:
        time.sleep(1)

signal.signal(signal.SIGUSR1, signal_handler)

# Iniciar un hilo secundario
t = threading.Thread(target=worker)
t.start()

print(f"🔧 PID del proceso: {os.getpid()}")
print("⏳ Enviá SIGUSR1 desde otra terminal con: kill -SIGUSR1 <PID>")
print("⌛ Esperando señal...")

while True:
    time.sleep(1)
