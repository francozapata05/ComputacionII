import argparse

def main():
    #Descripcion
    parser = argparse.ArgumentParser(description="Este script procesa archivos de texto.")

    #Argumentos
    parser.add_argument("-i", "--input", required=True, help="Nombre del Archivo de entrada")
    parser.add_argument("-o", "--output", default="salida.txt", help="Nombre del Archivo de salida")

    args = parser.parse_args()

    try:

        #Leer
        with open(args.input, "r") as archivo_entrada:
            texto = archivo_entrada.read()

        #Escribir
        with open(args.output, "w") as archivo_salida:
            archivo_salida.write(texto)

        #Mensaje exito
        print(f"El contenido de {args.input} ha sido guardado en {args.output}")

    except FileNotFoundError:
        print(f"No se pudo encontrar el archivo {args.input}")
    except Exception as e:
        print(f"Se produjo un error: {e}")


if __name__ == "__main__":
    main()