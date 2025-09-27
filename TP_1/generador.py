import os, time, datetime
import random, json

# Este programa genera datos de pacientes, colocandolos en las FIFOs

def formatear_datos(frecuencia, presion, oxigeno):
    # Damos formato json a los datos generados
    paciente = {
        "timestamp": datetime.datetime.now().timestamp(),  # float con segundos desde epoch
        "frecuencia": frecuencia,
        "presion": presion,
        "oxigeno": oxigeno
    }
    return json.dumps(paciente).encode()

def generador(i, FIFO_PATHS, a_listo, b_listo, c_listo, cantidad_pacientes):

    print("Generador: Comenzando")
    file_descriptors = []

    # Esperamos que se abran los extremos de lectura de las FIFO
    print("Esperando FIFOs...")
    a_listo.wait()
    b_listo.wait()
    c_listo.wait()
    
    try:

        # Abrir las FIFO en modo no-bloqueante
        for i in range(len(FIFO_PATHS)):
            fifo_path = FIFO_PATHS[i]
            file_descriptors.append(os.open(fifo_path, os.O_WRONLY | os.O_NONBLOCK))
        
        for _ in range(cantidad_pacientes):
            try:
                # Generar datos del paciente
                paciente = formatear_datos(
                    random.randint(60, 180),
                    [random.randint(110, 180), random.randint(70, 110)],
                    random.randint(90, 100)
                )
            except BlockingIOError:
                print("Generador: Error al generar datos.")

            try:
                # Escribir los datos en las FIFO
                for fifo_fd in file_descriptors:
                    os.write(fifo_fd, paciente + b"\n")
            except BlockingIOError:
                print("Generador: Error al escribir datos en las FIFO")
            
            time.sleep(0.2)
        for fifo_fd in file_descriptors:
            os.write(fifo_fd, json.dumps("FIN").encode())
        
    except Exception as e:
        print(f"Error Generador: {e}")
    finally:
        # Cerramos de forma segura todos los descriptores de archivo abiertos.
        print("Generador: Cerrando descriptores de FIFOs.")
        for fd in file_descriptors:
            try:
                os.close(fd)
            except OSError as e:
                # Omitir si ya fue cerrado o hay error al cerrar
                print(f"Generador: Error al cerrar descriptor {fd}: {e}")

        print("Generador: Proceso finalizado.")