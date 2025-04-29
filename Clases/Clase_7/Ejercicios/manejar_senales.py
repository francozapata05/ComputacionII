import signal
import time
import sys
import os

contador = 0

# Paso 1: Definir el handler
def manejar_ctrl_c(signum, frame):
    global contador
    contador += 1
    print(f"\n⚠️  Señal Nro: {contador}. SIGINT recibida. ¿Seguro que querés salir? (s/n): ", end="")
    respuesta = input()
    if respuesta.lower() == "s":
        print("🛑 Terminando el programa...")
        sys.exit(0)
    else:
        print("🔄 Continuando ejecución...")

def manejar_alarma(signum, frame):
    print("¡Se acabó el tiempo!")
    signal.alarm(5)

# Paso 2: Asignar handler a la señal SIGINT
signal.signal(signal.SIGINT, manejar_ctrl_c)
signal.signal(signal.SIGALRM, manejar_alarma)
signal.alarm(5)


# Paso 3: Bucle que simula trabajo continuo
print(f"⏳ {os.getpid()} El programa sigue corriendo... Presioná Ctrl+C para interrumpir.")
time.sleep(60)
