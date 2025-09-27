from multiprocessing import Process, Event, Queue
from analizador_generico import analizador_generico
from fifos import crear_fifos
from generador import generador
from verificador import verificador
from verificar_cadena import verificar_cadena, reporte_final

if __name__ == '__main__':

    FIFO_PATHS = [
        "/tmp/fifo_a",
        "/tmp/fifo_b",
        "/tmp/fifo_c"
    ]

    crear_fifos(FIFO_PATHS)

    fin_produccion = Event()
    a_listo = Event()
    b_listo = Event()
    c_listo = Event()
    cantidad_pacientes = 60 

    queues = [Queue() for _ in FIFO_PATHS]

    p1 = Process(target=generador, args=(1, FIFO_PATHS, a_listo, b_listo, c_listo, cantidad_pacientes))
    p2 = Process(target=analizador_generico, args=(FIFO_PATHS[0], "frecuencia", a_listo, queues[0]))
    p3 = Process(target=analizador_generico, args=(FIFO_PATHS[1], "presion", b_listo, queues[1]))
    p4 = Process(target=analizador_generico, args=(FIFO_PATHS[2], "oxigeno", c_listo, queues[2]))
    p5 = Process(target=verificador, args=(5, queues,))


    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()


    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()

    lista_corruptos = verificar_cadena()
    print(f"Lista de bloques corruptos: {lista_corruptos}")
    print("Verificador Blockchain: Terminado")
    reporte_final()
