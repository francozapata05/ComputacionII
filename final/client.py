import socket
import json
import argparse

def send_request(host, port, request_data):
    """Conecta, envía datos y retorna la respuesta del servidor."""
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            print(f"Conectado exitosamente a {sock.getpeername()}")
            sock.sendall(json.dumps(request_data).encode())
            response = sock.recv(4096)
            if not response:
                return {"error": "El servidor cerró la conexión sin una respuesta."}
            return json.loads(response.decode())
    except ConnectionRefusedError:
        return {"error": "No se pudo conectar al servidor. ¿Está corriendo?"}
    except Exception as e:
        return {"error": f"Ocurrió un error: {e}"}

def main():
    parser = argparse.ArgumentParser(
        description="Cliente para enviar URLs al servicio de análisis.",
        epilog="Ejemplo de uso:\n  python client.py --url http://example.com --host 127.0.0.1"
    )
    parser.add_argument("--url", required=True, help="La URL a analizar.")
    parser.add_argument("--host", default="localhost", help="El host del servidor (por defecto: localhost).")
    args = parser.parse_args()

    request_data = {
        "action": "analizar",
        "url": args.url
    }

    result = send_request(args.host, 9999, request_data)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
