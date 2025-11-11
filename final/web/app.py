from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from functools import wraps
from auth_client import autenticar_usuario
import socket
import json
import uuid

app = Flask(__name__)
app.secret_key = 'clave-secreta'

# Decorador para requerir inicio de sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Historial de tareas por usuario (en memoria)
user_tasks = {}

@app.before_request
def require_login():
    # Lista de endpoints que no requieren inicio de sesión
    allowed_routes = ['login', 'logout', 'static', 'index'] # 'index' is the function name for '/'

    if request.endpoint not in allowed_routes and 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('login'))

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        if autenticar_usuario(usuario, clave):
            session['usuario'] = usuario
            user_tasks.setdefault(usuario, [])  # Inicializa si no existe
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    usuario = session['usuario']

    # Si el usuario de la sesión no está en nuestro almacén en memoria (después de un reinicio), forzamos el re-login.
    if usuario not in user_tasks:
        flash("Tu sesión ha expirado o el servidor se ha reiniciado. Por favor, inicia sesión de nuevo.", "warning")
        session.pop('usuario', None)
        return redirect(url_for('login'))

    tareas = user_tasks.get(usuario, [])

    # Verificamos estado de tareas pendientes
    for t in tareas:
        if t['status'] == 'pending':
            r = consultar_resultado(t['task_id'])
            if r and r.get('status') == 'done':
                t['status'] = 'done'
                t['result'] = r.get('result')

    if request.method == 'POST':
        url = request.form['url']
        task_id = enviar_url_al_servidor(url)
        if task_id:
            tarea = {
                "task_id": task_id,
                "url": url,
                "status": "pending",
                "result": None
            }
            user_tasks[usuario].append(tarea)
            flash(f"Análisis iniciado con éxito. Task ID: {task_id}", "success")
        else:
            flash('Error: No se pudo enviar la URL al servidor de análisis.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', usuario=usuario, tareas=tareas)


@app.route('/check', methods=['GET', 'POST'])
@login_required
def check_task():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        if task_id:
            return redirect(url_for('resultado', task_id=task_id))
        else:
            flash("Por favor, ingrese un Task ID.", "warning")
            return redirect(url_for('check_task'))
    return render_template('check_task.html')


@app.route('/resultado/<task_id>')
@login_required
def resultado(task_id):
    usuario = session['usuario']
    tarea_encontrada = None
    
    # Busca la tarea en la lista del usuario actual
    if usuario in user_tasks:
        for tarea in user_tasks[usuario]:
            if tarea['task_id'] == task_id:
                tarea_encontrada = tarea
                break

    # Si la tarea se encontró pero está pendiente, intenta actualizarla
    if tarea_encontrada and tarea_encontrada.get('status') == 'pending':
        r = consultar_resultado(task_id)
        if r and r.get('status') == 'done':
            tarea_encontrada['status'] = 'done'
            tarea_encontrada['result'] = r.get('result')

    # Si la tarea no se encontró en la lista del usuario, intenta consultarla directamente
    if not tarea_encontrada:
        r = consultar_resultado(task_id)
        if r and r.get('status') == 'done':
            # Creamos un objeto 'tarea' temporal para la plantilla
            tarea_encontrada = {
                "task_id": task_id,
                "url": r.get('result', {}).get('url', 'N/A'),
                "status": "done",
                "result": r.get('result')
            }
    
    # Construye el objeto que espera la plantilla
    resultado_para_template = {}
    if tarea_encontrada and tarea_encontrada.get('status') == 'done':
        resultado_para_template = {
            "status": "done",
            "task_id": task_id,
            "result": tarea_encontrada.get('result')
        }

    return render_template('result.html', resultado=resultado_para_template, task_id=task_id)

@app.route('/tasks/status', methods=['POST'])
@login_required
def tasks_status():
    task_ids = request.json.get('task_ids', [])
    if not task_ids:
        return jsonify({})

    updated_tasks = {}
    usuario = session['usuario']

    if usuario in user_tasks:
        # Busca las tareas en la lista del usuario y actualiza su estado
        for tarea in user_tasks[usuario]:
            if tarea['task_id'] in task_ids and tarea['status'] == 'pending':
                r = consultar_resultado(tarea['task_id'])
                if r and r.get('status') == 'done':
                    tarea['status'] = 'done'
                    tarea['result'] = r.get('result')
                    updated_tasks[tarea['task_id']] = tarea['result']
    
    return jsonify(updated_tasks)

# -------------------------- TCP Helpers --------------------------

def enviar_url_al_servidor(url):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', 9999))
            request_data = { "action": "analizar", "url": url }
            sock.sendall(json.dumps(request_data).encode())
            response = sock.recv(4096)
            return json.loads(response.decode()).get('task_id')
    except (socket.error, json.JSONDecodeError, ConnectionRefusedError) as e:
        print(f"Error en enviar_url_al_servidor: {e}")
        return None

def consultar_resultado(task_id):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', 9999))
            request_data = { "action": "consultar", "task_id": task_id }
            sock.sendall(json.dumps(request_data).encode())
            response = sock.recv(4096)
            return json.loads(response.decode())
    except (socket.error, json.JSONDecodeError, ConnectionRefusedError) as e:
        print(f"Error en consultar_resultado: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, port=5000)