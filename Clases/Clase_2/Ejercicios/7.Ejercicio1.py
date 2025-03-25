import os
import time

#Ejercicio 1: Crear múltiples procesos hijos

def crear_hijos(num_hijos):

    for i in range(num_hijos):
        pid = os.fork()

        if pid == 0:  # Código del hijo
            print(f"Hijo {i+1} ({os.getpid()}) ejecutandose, padre: {os.getppid()}")
            exit(0)  # El hijo finaliza
        else:
            print(f"Padre ({os.getpid()}) creó al hijo {i + 1} (PID {pid})")

    # Espera a que todos los hijos terminen
    for _ in range(num_hijos):
        os.wait()

    print("Todos los hijos han finalizado")


if __name__ == "__main__":
    crear_hijos(5)