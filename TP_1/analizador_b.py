import json
from VentanaMovil import VentanaMovil

def analizador_b(i, fifo_path, b_listo, queue): 

    print("Analizador B: Comenzando")
    ventana = VentanaMovil(tiempo=30)

    # Avisamos al generador que el lector esta listo.
    b_listo.set()
    try:
        with open(fifo_path, 'r') as fifo:
            print("Abierta FIFO B...")

            while True:
                try:
                    linea = fifo.readline() # Leemos una linea del fichero
                except BlockingIOError:
                    print("Analizador B: Error al leer FIFO")
                data = json.loads(linea) # Convertimos a json
                if "FIN" in linea:  
                    break
                presion = data["presion"] # Obtenemos la presion, devuekve [sistolica, diastolica]
                try:
                    ventana.agregar(presion, data["timestamp"]) # Agregamos a la ventana
                except Exception as e:
                    print(f"Analizador B Error Ventana: {e}")
                try:
                    queue.put(ventana.formatear_datos("presion", data["timestamp"])) # Enviamos al verificador
                except Exception as e:
                    print(f"Analizador B Error Queue: {e}")

            print("Analizador B: Finalizado")
    
    except Exception as e:
        print(f"Analizador B: {e}")