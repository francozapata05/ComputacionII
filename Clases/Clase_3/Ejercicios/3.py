
import os
import random
import json


def main():
    primer_segundo_r,primer_segundo_w = os.pipe()

    pid = os.fork()

    if pid == 0: # Abuelo
        os.close(primer_segundo_r)
        
        numeros = []
        for i in range(10):
            numeros.append(random.randint(0,100))
        print(f"""Soy el abuelo. Los numeros son: {str(numeros)}""")

        os.write(primer_segundo_w, json.dumps(numeros).encode())


        os.close(primer_segundo_w)
        os._exit(0)

    else: #  

        segundo_tercero_r,segundo_tercero_w = os.pipe()
        pid2 = os.fork()

        if pid2 == 0: #  Padre
            os.close(primer_segundo_w)
            os.close(segundo_tercero_r)

            entrada = os.read(primer_segundo_r, 1024).decode()
            numeros = json.loads(entrada)

            print(f"""Soy el padre. He recibido los numeros: {numeros}""")

            pares = []
            for numero in numeros:
                if numero%2==0:
                    pares.append(numero)

            print(f"""Soy el padre. Los numeros pares son: {pares}""")
            os.write(segundo_tercero_w, json.dumps(pares).encode())
            os.close(segundo_tercero_w)

            os._exit(0)

        else: # Nieto 
            os.close(primer_segundo_r)
            os.close(primer_segundo_w)
            os.close(segundo_tercero_w)

            entrada = os.read(segundo_tercero_r, 1024).decode()
            lista_pares = json.loads(entrada)

            potencias = []
            for numero in lista_pares:
                potencias.append(numero**2)
            print(f"""Soy el nieto. Los potencias son: {potencias}""")

            os._exit(0)

if __name__ == "__main__":
    main()



