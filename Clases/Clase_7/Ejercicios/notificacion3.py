import os
import signal
import time
import sys

# Variables globales
señal_de_nieto = False
señal_de_hijo = False

# Handler del padre
def handler_padre(signum, frame):
    global señal_de_hijo
    señal_de_hijo = True
    print("👨 Padre: recibí señal del hijo.")

# Handler del hijo
def handler_hijo(signum, frame):
    global señal_de_nieto
    señal_de_nieto = True
    print("👦 Hijo: recibí señal del nieto.")

# Registrar handler en el padre
signal.signal(signal.SIGUSR1, handler_padre)

# Crear proceso hijo
pid_hijo = os.fork()

if pid_hijo == 0:
    # Código del hijo
    signal.signal(signal.SIGUSR2, handler_hijo)  # Recibe de nieto

    # Crear proceso nieto
    pid_nieto = os.fork()

    if pid_nieto == 0:
        # Código del nieto
        print("🧒 Nieto: esperando 2 segundos...")
        time.sleep(2)
        print("🧒 Nieto: enviando SIGUSR2 al hijo.")
        os.kill(os.getppid(), signal.SIGUSR2)
        sys.exit(0)
    else:
        print("👦 Hijo: esperando señal del nieto...")
        while not señal_de_nieto:
            signal.pause()
        print("👦 Hijo: señal recibida. Ahora aviso al padre.")
        os.kill(os.getppid(), signal.SIGUSR1)
        os.wait()  # Espera al nieto
        sys.exit(0)
else:
    print("👨 Padre: esperando señal del hijo...")
    while not señal_de_hijo:
        signal.pause()
    print("✅ Padre: ¡La cadena de señales se completó con éxito!")
    os.wait()  # Espera al hijo
