import os

def crear_fifos(FIFO_PATHS):
    """Crea los FIFOs necesarios con permisos adecuados"""
    for path in FIFO_PATHS:
        try:
            if os.path.exists(path):
                os.unlink(path)
            os.mkfifo(path, mode=0o666)
            print(f"FIFO creado: {path}")
        except Exception as e:
            print(f"Error creando FIFO {path}: {e}")
