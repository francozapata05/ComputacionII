import os
import signal
import time
import sys

def handler(signum, frame):
    print("\n⚠️  Señal SIGUSR1 recibida.", end="")


signal.signal(signal.SIGUSR1, handler)

pid = os.fork()

if pid == 0:
    print("⏳ Soy el hijo.")
    i = 0
    while i < 10000:
        i += 1
        print(f"⏳ Contando... {i}...")
    print("⏳ Hijo enviando señal al padre...")
    os.kill(os.getppid(), signal.SIGUSR1)
    print("⏳ Mi hijo terminó.")
    os._exit(0)
else:
    print("⏳ Mi padre esperando señal de mi hijo...")
    signal.pause()
    print("\n ⏳ Padre: señal recibida...")
