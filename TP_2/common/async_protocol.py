import json
import struct

async def async_recibir_mensaje_completo(reader):
    """Lee un mensaje del StreamReader usando el protocolo de prefijo de longitud."""
    raw_msglen = await reader.readexactly(8)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>Q', raw_msglen)[0]

    data = b''
    while len(data) < msglen:
        packet = await reader.read(min(msglen - len(data), 4096))
        if not packet:
            #Imagina que el emisor debe enviar un mensaje de 1000 bytes, pero se bloquea y cierra la conexión después de enviar solo 500 bytes.
            return None
        data += packet
    return data

async def async_enviar_mensaje_completo(writer, mensaje_dict):
    """Codifica y envía un mensaje al StreamWriter usando el protocolo de prefijo de longitud."""
    mensaje_json = json.dumps(mensaje_dict).encode('utf-8')
    mensaje_len = struct.pack('>Q', len(mensaje_json))
    writer.write(mensaje_len + mensaje_json)
    await writer.drain() # Asegura que los datos se envíen
