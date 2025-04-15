import os
import time

# Codigo usando fork que hable entre procesos atraves 
# de archivos temporales pero que busquen evidenciar 
# los tipos de problemas que tiene esta comunicacion

def main():
    file_name = "comunicacion.txt"

    # Crear el archivo si no existe
    file = os.open(file_name, os.O_CREAT | os.O_RDWR, 0o644)
    os.close(file)  # Lo cerramos porque vamos a abrirlo en los procesos

    create_child(file_name, "Soy el hijo 1")
    create_child(file_name, "Soy el hijo 2")

def create_child(file_name, message):
    pid = os.fork()

    if pid == 0:
        # Hijo
        print(f"{message}, mi PID es {os.getpid()}, el id de mi padre es {os.getppid()}")
        # ¡Abrir el archivo correctamente!
        file = os.open(file_name, os.O_WRONLY | os.O_APPEND)
        texto = f"{message}, mi PID es {os.getpid()}, el id de mi padre es {os.getppid()}\n"
        os.write(file, texto.encode())
        os.close(file)
        os._exit(0)

    # Padre
    os.wait()
    file = os.open(file_name, os.O_RDONLY)
    contenido = os.read(file, 1024).decode()
    os.close(file)
    print(f"[Padre] Contenido leído:\n{contenido}")


if __name__ == "__main__":
    main()