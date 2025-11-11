import socket
import json
import argparse

def send_request(request_data):
    """Conecta, envía datos y retorna la respuesta del servidor."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", 9999))
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
        epilog="Ejemplo de uso:\n  python client.py --url http://example.com"
    )
    parser.add_argument("--url", required=True, help="La URL a analizar.")
    args = parser.parse_args()

    request_data = {
        "action": "analizar",
        "url": args.url
    }

    result = send_request(request_data)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
