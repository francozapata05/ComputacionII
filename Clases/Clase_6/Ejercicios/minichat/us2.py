# user2.py
import os
import sys
import select

fifo_write = "/tmp/chat2to1"
fifo_read = "/tmp/chat1to2"

# Crear los FIFOs si no existen
for path in [fifo_write, fifo_read]:
    if not os.path.exists(path):
        os.mkfifo(path)

# Abrimos los dos extremos para evitar bloqueos
fd_read = os.open(fifo_read, os.O_RDONLY | os.O_NONBLOCK)
fd_write_dummy = os.open(fifo_read, os.O_WRONLY | os.O_NONBLOCK)

fd_write = os.open(fifo_write, os.O_WRONLY | os.O_NONBLOCK)
fd_read_dummy = os.open(fifo_write, os.O_RDONLY | os.O_NONBLOCK)

print("🟢 Chat activo (User 2). Escribí algo o esperá mensaje...")

while True:
    rlist, _, _ = select.select([fd_read, sys.stdin], [], [])
    for ready in rlist:
        if ready == fd_read:
            try:
                data = os.read(fd_read, 1024)
                if data:
                    print(f"\nUser1: {data.decode()}")
                else:
                    print("\n🔴 El otro usuario cerró el chat.")
                    exit(0)
            except BlockingIOError:
                continue
        elif ready == sys.stdin:
            mensaje = input("User2: ")
            os.write(fd_write, mensaje.encode())
