
#Ejercicio 3: Servidor multiproceso simple

import os
import time

def manejar_cliente(cliente_id):
    print(f"Cliente {cliente_id} atendido por proceso {os.getpid()}")
    time.sleep(3)  # Simula tiempo de atención
    print(f"Cliente {cliente_id} atendido completamente.")

num_clientes = 5

for i in range(num_clientes):
    pid = os.fork()
    if pid == 0:  # Código del hijo
        manejar_cliente(i + 1)
        exit(0)  # Finaliza el hijo correctamente

# El padre espera a todos los hijos
for i in range(num_clientes):
    os.wait()

print("Todos los clientes fueron atendidos.")
