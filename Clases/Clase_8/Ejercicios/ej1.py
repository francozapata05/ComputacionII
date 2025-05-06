from multiprocessing import Process
import os, time

def tarea():
    time.sleep(10)
    print(f"Proceso hijo ejecutándose. PID: {os.getpid()}")

if __name__ == "__main__":
    print(f"Proceso principal. PID: {os.getpid()}")
    p = Process(target=tarea)
    print(p.pid)
    p.start()
    print(p.pid)
    print("Post start------------------")
    time.sleep(20)
    p.join()
    time.sleep(10)
    print("El proceso hijo ha terminado.")
