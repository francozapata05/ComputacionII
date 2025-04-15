
# Ejercicio 2: Contador de Palabras
# Implementa un sistema donde el proceso padre lee un 
# archivo de texto y envía su contenido línea por línea 
# a un proceso hijo a través de un pipe. 
# El hijo debe contar las palabras en cada línea y 
# devolver el resultado al padre.

import os

def main():
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid != 0:  # PADRE
        os.close(padre_a_hijo_r)
        os.close(hijo_a_padre_w)

        with open("/home/franco/Desktop/ComputacionII/Clases/Clase_3/Ejercicios/texto.txt", "r") as texto:
            for linea in texto:
                os.write(padre_a_hijo_w, linea.encode())

        os.close(padre_a_hijo_w)

        mensaje_final = os.read(hijo_a_padre_r, 1024).decode()
        os.close(hijo_a_padre_r)

        print("Resultado del hijo:\n" + mensaje_final)

    else:  # HIJO
        os.close(hijo_a_padre_r)
        os.close(padre_a_hijo_w)

        entrada = os.read(padre_a_hijo_r, 1024).decode()
        os.close(padre_a_hijo_r)

        resultado = ""
        for i, linea in enumerate(entrada.strip().split("\n"), 1):
            palabras = len(linea.strip().split())
            resultado += f"Línea {i}: {palabras} palabras\n"

        os.write(hijo_a_padre_w, resultado.encode())
        os.close(hijo_a_padre_w)

        os._exit(0)

if __name__ == "__main__": 
    main()
