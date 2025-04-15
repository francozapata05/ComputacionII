#Ejercicio 1: Eco Simple
#Crea un programa en Python que establezca comunicación entre un 
# proceso padre y un hijo mediante un pipe. 
# El padre debe enviar un mensaje al hijo, y el hijo debe recibir ese mensaje 
# y devolverlo al padre (eco).

import os
import sys

def main():
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid != 0:  # Padre
        os.close(padre_a_hijo_r)
        os.close(hijo_a_padre_w)

        os.write(padre_a_hijo_w, b"Yo soy tu padre.")
        os.close(padre_a_hijo_w)

        mensaje = os.read(hijo_a_padre_r, 1024)
        os.close(hijo_a_padre_r)

        print(mensaje.decode())

    else:  # Hijo
        os.close(hijo_a_padre_r)
        os.close(padre_a_hijo_w)

        mensaje = os.read(padre_a_hijo_r, 1024)
        os.close(padre_a_hijo_r)

        os.write(hijo_a_padre_w, mensaje)
        os.close(hijo_a_padre_w)

        os._exit(0)

if __name__ == "__main__":
    main()
