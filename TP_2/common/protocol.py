import json
import struct

def recibir_mensaje_completo(conn):
    """Lee un mensaje del socket usando el protocolo de prefijo de longitud."""
    raw_msglen = conn.recv(8)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>Q', raw_msglen)[0]

    data = b''
    while len(data) < msglen:
        packet = conn.recv(4096)
        if not packet:
            return None
        data += packet
    return data

def enviar_mensaje_completo(conn, mensaje_dict):
    """Codifica y envía un mensaje usando el protocolo de prefijo de longitud."""
    mensaje_json = json.dumps(mensaje_dict).encode('utf-8')
    mensaje_len = struct.pack('>Q', len(mensaje_json))
    conn.sendall(mensaje_len + mensaje_json)
