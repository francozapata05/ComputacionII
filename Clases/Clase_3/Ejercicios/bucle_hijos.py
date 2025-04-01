import os
import time


print(f"Proceso nivel 1, PID: {os.getpid()}, PPID: {os.getppid()}")
pid = os.fork()

if pid == 0:
    print(f"Proceso nivel 2, PID: {os.getpid()}, PPID: {os.getppid()}")
    pid = os.fork()

    if pid == 0:
        print(f"Proceso nivel 3, PID: {os.getpid()}, PPID: {os.getppid()}")
        pid = os.fork()

        if pid == 0:
            print(f"Proceso nivel 4, PID: {os.getpid()}, PPID: {os.getppid()}")
            pid = os.fork()

            if pid == 0:
                print(f"Proceso nivel 5, PID: {os.getpid()}, PPID: {os.getppid()}")
                time.sleep(2)
                print(f"Proceso nivel 5, PID: {os.getpid()}, finalizando")
            else:
                print(f"Proceso nivel 4, PID: {os.getpid()}, finalizando")
        else:
            print(f"Proceso nivel 3, PID: {os.getpid()}, finalizando")
    else:
        print(f"Proceso nivel 2, PID: {os.getpid()}, finalizando")
else:
    print(f"Proceso nivel 1, PID: {os.getpid()}, finalizando")
