import json
from VentanaMovil import VentanaMovil
from multiprocessing import Event, Queue 
import os 

def analizador_generico(fifo_path: str, signal_name: str, listo_event, queue: Queue):
    """
    Proceso genérico para analizar una señal específica de los datos biométricos.
    """
    
    print(f"Analizador ({signal_name.capitalize()}): Comenzando")
    ventana = VentanaMovil(tiempo=30)
    
    # Avisamos al generador que el lector está listo.
    listo_event.set() 

    try:
        print(f"Abriendo FIFO para {signal_name.capitalize()}...")

        with open(fifo_path, 'r') as fifo:
            print(f"Abierta FIFO para {signal_name.capitalize()}...")
            
            while True:
                try:
                    # Leemos una línea.
                    linea = fifo.readline() 
                except BlockingIOError:
                    print(f"Analizador ({signal_name.capitalize()}): Error al leer FIFO (BlockingIOError)")
                    continue # Reintentar
                    
                if not linea:
                    # Si readline() devuelve una cadena vacía, el escritor (generador) cerró su descriptor.
                    # Asumiendo que el 'FIN' se envía justo antes de cerrar, lo manejaremos a continuación.
                    continue 

                if "FIN" in linea:
                    print(f"Analizador ({signal_name.capitalize()}): Recibido mensaje de FIN")
                    break
                
                try:
                    data = json.loads(linea) # Convertimos a json
                except json.JSONDecodeError as e:
                    print(f"Analizador ({signal_name.capitalize()}): Error de JSON al decodificar: {e} en línea: {linea.strip()}")
                    continue

                # Extraemos la señal usando la variable signal_name
                signal_value = data[signal_name] 
                
                
                try:
                    ventana.agregar(signal_value, data["timestamp"]) 
                except Exception as e:
                    print(f"Analizador ({signal_name.capitalize()}) Error Ventana: {e}")

                try:
                    # Enviamos al verificador el resultado
                    queue.put(ventana.formatear_datos(signal_name, data["timestamp"])) 
                except Exception as e:
                    print(f"Analizador ({signal_name.capitalize()}) Error Queue: {e}")

            print(f"Analizador ({signal_name.capitalize()}): Finalizado")
    
    except Exception as e:
        print(f"Analizador ({signal_name.capitalize()}) Error General: {e}")