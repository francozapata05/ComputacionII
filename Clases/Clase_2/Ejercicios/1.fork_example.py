import os

def crear_proceso():
    pid = os.fork()  # Crear un nuevo proceso

    if pid == 0:
        print(f"Soy el proceso hijo, mi PID es {os.getpid()} y mi padre tiene PID {os.getppid()}")

    else:
        print(f"Soy el proceso padre, mi PID es {os.getpid()} y mi hijo tiene PID {pid}")

if __name__ == "__main__":
    crear_proceso()
