import json
from VentanaMovil import VentanaMovil

def analizador_a(i, fifo_path, a_listo, queue):

    print("Analizador A: Comenzando")
    ventana = VentanaMovil(tiempo=30)

    # Avisamos al generador que el lector esta listo.
    a_listo.set()

    try:
        print("Abriendo FIFO A...")
        with open(fifo_path, 'r') as fifo:
            print("Abierta FIFO A...")

            while True:
                try:
                    linea = fifo.readline() # Leemos una linea del fichero
                except BlockingIOError:
                    print("Analizador A: Error al leer FIFO")
                data = json.loads(linea) # Convertimos a json
                if "FIN" in linea:
                    break
                frecuencia = data["frecuencia"] # Obtenemos la frecuencia
                try:
                    ventana.agregar(frecuencia, data["timestamp"]) # Agregamos a la ventana
                except Exception as e:
                    print(f"Analizador A Error Ventana: {e}")
                try:
                    queue.put(ventana.formatear_datos("frecuencia", data["timestamp"])) # Enviamos al verificador
                except Exception as e:
                    print(f"Analizador A Error Queue: {e}")


            print("Analizador A: Finalizado")
    
    except Exception as e:
        print(f"Analizador A: {e}")