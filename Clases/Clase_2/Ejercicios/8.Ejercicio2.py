
# Ejercicio 2: Crear un proceso y ejecutarle un programa

import os

pid = os.fork()

if pid == 0:  # Código del hijo
    print(f"Hijo ({os.getpid()}) ejecutando un script con exec")
    os.execlp("python3", "python3", "script.py")
else:
    os.wait()  # El padre espera al hijo
    print("El hijo ha terminado.")


