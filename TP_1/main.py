import os, json, datetime, random

from multiprocessing import Process, Event, Queue

from fifos import crear_fifos
from generador import generador
from analizador_a import analizador_a
from analizador_b import analizador_b
from analizador_c import analizador_c
from verificador import verificador
from verificar_cadena import verificar_cadena

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
    p2 = Process(target=analizador_a, args=(2, FIFO_PATHS[0], a_listo, queues[0]))
    p3 = Process(target=analizador_b, args=(3, FIFO_PATHS[1], b_listo, queues[1]))
    p4 = Process(target=analizador_c, args=(4, FIFO_PATHS[2], c_listo, queues[2]))
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

