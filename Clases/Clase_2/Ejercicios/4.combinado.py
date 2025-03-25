import os

pid = os.fork()

if pid == 0:  # Código del hijo
    print(f"Soy el hijo ({os.getpid()}), ejecutando 'date'...")
    os.execlp("date", "date")  # Reemplaza el proceso hijo con 'date'
    os.execlp("whoami, whoami")  
    print("Prueba post exec")
    print("Esto no debería aparecer")
else:
    print(f"Soy el padre ({os.getpid()}), esperando a mi hijo ({pid})")
    os.wait()  # Espera a que el hijo termine
