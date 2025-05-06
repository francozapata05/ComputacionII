import os
import sys, time

def main():
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()

    pid = os.fork()

    if pid != 0:  # Padre
        os.close(padre_a_hijo_r)

        os.write(padre_a_hijo_w, b"Yo soy tu padre.")
        print(os.getpid())
        time.sleep(30)
        os.close(padre_a_hijo_w)

        print(mensaje.decode())

    else:  # Hijo
        os.close(padre_a_hijo_w)

        mensaje = os.read(padre_a_hijo_r, 1024)
        time.sleep(30)
        os.close(padre_a_hijo_r)

        os._exit(0)

if __name__ == "__main__":
    main()
