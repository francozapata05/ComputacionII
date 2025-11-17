import socket
import json
import os

# La ruta del socket debe ser la misma que en auth_process.py
SOCKET_FILE = "/tmp/auth_service.sock"

def _send_request(request_data):
    """
    Función genérica para enviar una petición al proceso de autenticación
    a través de un socket TCP.
    """
    try:
        # Usamos el nombre del servicio 'auth_service' que Docker resuelve a la IP del contenedor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('auth_service', 9998))
            sock.sendall(json.dumps(request_data).encode())
            
            response_raw = sock.recv(4096)
            if not response_raw:
                return {"status": "error", "message": "No se recibió respuesta del servicio de autenticación."}
                
            return json.loads(response_raw.decode())
    except (socket.error, json.JSONDecodeError, ConnectionRefusedError) as e:
        print(f"Error comunicándose con el servicio de autenticación: {e}")
        return {"status": "error", "message": "No se pudo conectar con el servicio de autenticación."}

def register_user(email, password):
    """Envía una petición de registro al auth_process."""
    return _send_request({
        "action": "register",
        "email": email,
        "password": password
    })

def login_user(email, password):
    """
    Envía una petición de login al auth_process.
    Devuelve el diccionario de respuesta completo.
    """
    return _send_request({
        "action": "login",
        "email": email,
        "password": password
    })