import socket
import json
import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from database.models import db, User

# ==========================================================
# Configuración de la Aplicación y Base de Datos
# ==========================================================

def create_app_context():
    """Crea un contexto de aplicación Flask para interactuar con la base de datos."""
    app = Flask(__name__)
    
    # Asegurarse de que la variable de entorno DATABASE_URL esté disponible
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Error: La variable de entorno DATABASE_URL no está configurada.", file=sys.stderr)
        sys.exit(1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app_context()

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen."""
    with app.app_context():
        db.create_all()
    print("Base de datos inicializada y tablas creadas.")

# ==========================================================
# Lógica de Negocio de Autenticación
# ==========================================================

def handle_request(data):
    """Procesa las solicitudes de registro y login."""
    action = data.get('action')
    email = data.get('email')
    password = data.get('password')

    if not all([action, email, password]):
        return {'status': 'error', 'message': 'Faltan parámetros en la solicitud.'}

    if action == 'register':
        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first():
            return {'status': 'error', 'message': 'El correo electrónico ya está registrado.'}
        
        # Crear nuevo usuario
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return {'status': 'success', 'message': 'Usuario registrado con éxito.'}

    elif action == 'login':
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Devolver datos del usuario para la sesión
            return {
                'status': 'success',
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            }
        else:
            return {'status': 'error', 'message': 'Credenciales inválidas.'}
    
    else:
        return {'status': 'error', 'message': 'Acción no válida.'}

# ==========================================================
# Servidor de Sockets UNIX
# ==========================================================

def run_socket_server():
    """Inicia el servidor de sockets para escuchar peticiones."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9998))
    server.listen(5)
    print("Servidor de autenticación escuchando en el puerto 9998")

    try:
        while True:
            conn, addr = server.accept()
            print(f"Conexión aceptada de {addr}")
            try:
                while True:
                    raw_data = conn.recv(4096)
                    if not raw_data:
                        break
                    
                    request_data = json.loads(raw_data.decode())
                    
                    with app.app_context():
                        response = handle_request(request_data)
                    
                    conn.sendall(json.dumps(response).encode())
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error procesando la solicitud: {e}", file=sys.stderr)
                error_response = json.dumps({'status': 'error', 'message': 'Solicitud mal formada.'})
                conn.sendall(error_response.encode())
            finally:
                conn.close()
    except KeyboardInterrupt:
        print("Cerrando el servidor de autenticación.")
    finally:
        server.close()

if __name__ == '__main__':
    init_db()
    run_socket_server()
