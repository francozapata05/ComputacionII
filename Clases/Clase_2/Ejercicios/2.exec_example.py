import os

def ejecutar_ls():
    pid = os.fork()

    if pid == 0:  # Código del hijo
        print(f"Soy el hijo ({os.getpid()}), ejecutando 'ls -l'...")
        os.execlp("ls", "ls", "-l")  # Reemplaza el proceso con ls -l
        os.execlp("ping", "ping", "-c", "4", "google.com")  # Reemplaza el proceso con ping
    else:
        print(f"Soy el padre ({os.getpid()}), esperando a mi hijo ({pid})")

if __name__ == "__main__":
    ejecutar_ls()
