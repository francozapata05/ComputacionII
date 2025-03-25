import os

def esperar_hijo():
    pid = os.fork()

    if pid == 0:
        id_hijo = os.getpid()
        print(f"Soy el hijo ({id_hijo}), trabajando...")
        os._exit(0)  # Termina el proceso hijo
    else:
        id_padre = os.getpid()
        print(f"Soy el padre ({id_padre}), esperando a mi hijo ({pid})...")
        os.wait()  # Espera a que el hijo termine
        print(f"El hijo ({pid}) ha terminado.")

if __name__ == "__main__":
    esperar_hijo()
