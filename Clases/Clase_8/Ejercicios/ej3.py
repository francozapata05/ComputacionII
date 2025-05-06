# Que pasa con ls -l con el Pipe usando multiprocessing

from multiprocessing import Process, Pipe
import time

def hijo(conn):
    conn.send("Hola desde el proceso hijo")
    print(p.pid)
    time.sleep(10)
    conn.close()

if __name__ == "__main__":
    padre_conn, hijo_conn = Pipe()
    p = Process(target=hijo, args=(hijo_conn,))
    p.start()
    print(padre_conn.recv())  # Espera recibir algo del hijo
    p.join()
