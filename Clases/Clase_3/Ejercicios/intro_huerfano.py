import os
import time

def create_child(sleep, message):
    pid = os.fork()
    if pid == 0:
        time.sleep(sleep)
        print(f"{message}, mi PID es {os.getpid()}, el id de mi padre es {os.getppid()}")
        os._exit(0)  # Termina el proceso hijo


def main():
    create_child(2, "Soy el hijo 1")
    create_child(3, "Soy el hijo 2")
    
    time.sleep(1)
    print(f"Soy el padre, mi PID es {os.getpid()}")
    os._exit(0)  # Termina el proceso padre

if __name__ == "__main__":
    main()
