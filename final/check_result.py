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
        description="Cliente para consultar el resultado de un análisis de URL.",
        epilog="Ejemplo de uso:\n  python check_result.py --task-id <ID_de_la_tarea>"
    )
    parser.add_argument("--task-id", required=True, help="El ID de la tarea a consultar.")
    args = parser.parse_args()

    request_data = {
        "action": "consultar",
        "task_id": args.task_id
    }

    result = send_request(request_data)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

