import sys
import getopt

# Ejemplo usando solo sys.argv
""" 
print("Argumentos recibidos:", sys.argv)
 """


# Ejemplo usando getopt

"""
import sys
import getopt

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:a:", ["help", "name=", "age="])
    except getopt.GetoptError as err:
        print(f"Error: {err}")
        sys.exit(1)

    name = None
    age = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Uso: script.py -n <nombre> -a <edad>")
            sys.exit()
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-a", "--age"):
            age = arg

    if name and age:
        print(f"Hola, {name}. Tienes {age} años.")
    else:
        print("Faltan argumentos. Usa -h para ver la ayuda.")

if __name__ == "__main__":
    main()

"""

# Ejemplo usando solo Argparse

"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Este script muestra un saludo con nombre y edad.")

    parser.add_argument("-n", "--name", required=True, help="Nombre de la persona")
    parser.add_argument("-a", "--age", type=int, required=True, help="Edad de la persona")

    args = parser.parse_args()

    print(f"Hola, {args.name}. Tienes {args.age} años.")

if __name__ == "__main__":
    main()
"""