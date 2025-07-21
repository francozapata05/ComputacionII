import json
from VentanaMovil import VentanaMovil

def analizador_c(i, fifo_path, c_listo, queue): 

    print("Analizador C: Comenzando")
    ventana = VentanaMovil(tiempo=30)

    # Avisamos al generador que el lector esta listo.
    c_listo.set()

    try:
        with open(fifo_path, 'r') as fifo:
            print("Abierta FIFO C...")

            while True:
                try:
                    linea = fifo.readline() # Leemos una linea del fichero
                except BlockingIOError:
                    print("Analizador C: Error al leer FIFO")
                data = json.loads(linea) # Convertimos a json
                if "FIN" in linea:
                    break
                oxigeno = data["oxigeno"] # Obtenemos la oxigeno
                try:
                    ventana.agregar(oxigeno, data["timestamp"]) # Agregamos a la ventana
                except Exception as e:
                    print(f"Analizador C Error Ventana: {e}")
                try:
                    queue.put(ventana.formatear_datos("oxigeno", data["timestamp"])) # Enviamos al verificador
                except Exception as e:
                    print(f"Analizador C Error Queue: {e}")
                
            print("Analizador C: Finalizado")
    
    except Exception as e:
        print(f"Analizador C: {e}")