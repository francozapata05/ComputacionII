import os
import time
import tempfile

# Codigo usando fork que hable entre procesos atraves 
# de archivos temporales pero que busquen evidenciar 
# los tipos de problemas que tiene esta comunicacion

def main():
    file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    file_name = file.name
    file.close()
    create_children(file, file_name, "Soy el hijo 1")
    create_children(file, file_name, "Soy el hijo 2")

def create_children(file, file_name, message):
    pid = os.fork()
    if pid == 0:
        print(f"{message}, mi PID es {os.getpid()}, el id de mi padre es {os.getppid()}")
        os._exit(0)  # Termina el proceso hijo
    
    with open(file_name, 'r') as f:
        contenido = f.read()
        print(f"Contenido leido: {contenido}")
        
    file.write(f"{message}, leyendo el archivo, mi PID es {os.getpid()}, el id de mi padre es {os.getppid()}\n")


if __name__ == "__main__":
    main()
