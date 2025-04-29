import os

fifo_write = "/tmp/chat2to1"
fifo_read = "/tmp/chat1to2"

if not os.path.exists(fifo_write):
    os.mkfifo(fifo_write)

if not os.path.exists(fifo_read):
    os.mkfifo(fifo_read)

# Abrir FIFO
fd_read = os.open(fifo_read, os.O_RDONLY)
fd_write = os.open(fifo_write, os.O_WRONLY)

# Leer primero
mensaje = os.read(fd_read, 1024)
print(f"Otro: {mensaje.decode()}")

# Escribir respuesta
mensaje = input("Vos: ")
os.write(fd_write, mensaje.encode())
