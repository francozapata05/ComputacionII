import os
import signal
import time
import sys

# Variables globales para saber quién terminó primero
hijo1_termino = False
hijo2_termino = False

def handler1(signum, frame):
    global hijo1_termino
    hijo1_termino = True
    print("\n⚠️  Señal SIGUSR1 recibida: terminó hijo1.")

def handler2(signum, frame):
    global hijo2_termino
    hijo2_termino = True
    print("\n⚠️  Señal SIGUSR2 recibida: terminó hijo2.")

# Registrar handlers
signal.signal(signal.SIGUSR1, handler1)
signal.signal(signal.SIGUSR2, handler2)

# Crear hijo 1
pid1 = os.fork()

if pid1 == 0:
    print("👦 Hijo1: empezando tarea pesada...")
    for i in range(1, 100000):
        _ = i * i  # Simular carga
    print("👦 Hijo1: enviando SIGUSR1 al padre.")
    os.kill(os.getppid(), signal.SIGUSR1)
    sys.exit(0)

# Crear hijo 2
pid2 = os.fork()

if pid2 == 0:
    print("👦 Hijo2: esperando 3 segundos...")
    time.sleep(3)
    print("👦 Hijo2: enviando SIGUSR2 al padre.")
    os.kill(os.getppid(), signal.SIGUSR2)
    sys.exit(0)

# Proceso padre
print("👨 Padre esperando señales de los hijos...\n")

# Espera ambas señales
while not (hijo1_termino and hijo2_termino):
    signal.pause()

print("\n✅ Ambos hijos han terminado.")
if hijo1_termino and not hijo2_termino:
    print("🔔 Hijo1 terminó primero.")
elif hijo2_termino and not hijo1_termino:
    print("🔔 Hijo2 terminó primero.")
else:
    print("🟰 Ambos terminaron casi al mismo tiempo.")

# Espera a que los hijos terminen realmente
os.wait()
os.wait()
