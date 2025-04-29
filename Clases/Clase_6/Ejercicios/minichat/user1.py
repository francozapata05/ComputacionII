import os
import select

# Hacer una implementacion simple de chat donde el que comience a escribir pueda ser
# cualquiera (usando 2 fifos, bajo nivel) y no se bloquee innecesariamente

fifo_write = "/tmp/chat1to2"
fifo_read = "/tmp/chat2to1"

if not os.path.exists(fifo_write):
    os.mkfifo(fifo_write)

if not os.path.exists(fifo_read):
    os.mkfifo(fifo_read)


# Abrir Fifo
fd_write = os.open(fifo_write, os.O_WRONLY)
fd_read =os.open(fifo_read, os.O_RDONLY)

# Enviar mensaje
mensaje = input("Vos: ")
os.write(fd_write,mensaje.encode())

# Leer respuesta
respuesta = os.read(fd_read, 1024).decode()
print(f"Otro: {respuesta}")
