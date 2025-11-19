from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from functools import wraps
from app.auth_client import register_user, login_user
import socket
import json
import os
from database.models import db, User, Search
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-key-debes-cambiarla-en-produccion')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ==========================================================
# Decoradores y Control de Acceso
# ==========================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================================
# Rutas de la Aplicación
# ==========================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(  f"Registro: email={email}, password={password }")

        if not email or not password:
            flash('Email and password are required.', 'warning')
            return render_template('register.html')

        response = register_user(email, password)
        
        if response.get('status') == 'success':
            flash('Registration successful. Now you can log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(response.get('message', 'An error occurred during registration.'), 'danger')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        response = login_user(email, password)

        if response.get('status') == 'success':
            user_data = response.get('user', {})
            session['user_id'] = user_data.get('id')
            session['user_email'] = user_data.get('email')
            flash('Logged in Successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(response.get('message', 'Invalid Credentials'), 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_id = session['user_id']
    
    if request.method == 'POST':
        url = request.form['url']
        task_id = enviar_url_al_servidor(url)
        if task_id:
            new_search = Search(
                task_id=task_id,
                url=url,
                status="pending",
                user_id=user_id
            )
            db.session.add(new_search)
            db.session.commit()
            flash(f"Analysis for {url} started successfully. Task ID: {task_id}", "success")
        else:
            flash('Error: Could not send URL to analysis server.', 'danger')
        return redirect(url_for('dashboard'))

    # GET request
    searches = Search.query.filter_by(user_id=user_id).order_by(Search.date.desc()).all()
    
    # Verificamos estado de tareas pendientes
    needs_commit = False
    for search in searches:
        if search.status == 'pending':
            result_data = consultar_resultado(search.task_id)
            if result_data and result_data.get('status') == 'done':
                _update_search_details(search, result_data.get('result', {}))
                needs_commit = True
    
    if needs_commit:
        db.session.commit()

    return render_template('dashboard.html', user_email=session.get('user_email'), searches=searches)

@app.route('/check', methods=['GET', 'POST'])
@login_required
def check_task():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        if task_id:
            return redirect(url_for('resultado', task_id=task_id))
        else:
            flash("Please enter a Task ID.", "warning")
            return redirect(url_for('check_task'))
    return render_template('check_task.html')

@app.route('/resultado/<task_id>')
@login_required
def resultado(task_id):
    user_id = session['user_id']
    search = Search.query.filter_by(task_id=task_id, user_id=user_id).first()

    if not search:
        flash("Task ID not found or you do not belong to it.", "danger")
        return redirect(url_for('dashboard'))

    if search.status == 'pending':
        result_data = consultar_resultado(task_id)
        if result_data and result_data.get('status') == 'done':
            _update_search_details(search, result_data.get('result', {}))
            db.session.commit()

    return render_template('result.html', search=search)

@app.route('/tasks/status', methods=['POST'])
@login_required
def tasks_status():
    task_ids = request.json.get('task_ids', [])
    if not task_ids:
        return jsonify({})

    user_id = session['user_id']
    searches = Search.query.filter(
        Search.user_id == user_id,
        Search.task_id.in_(task_ids),
        Search.status == 'pending'
    ).all()

    updated_tasks = {}
    needs_commit = False
    for search in searches:
        result_data = consultar_resultado(search.task_id)
        if result_data and result_data.get('status') == 'done':
            result_details = result_data.get('result', {})
            _update_search_details(search, result_details)
            needs_commit = True
            updated_tasks[search.task_id] = {
                'title': search.title,
                'description': search.description,
                'status': search.status,
                'time': search.loading_time
            }
    
    if needs_commit:
        db.session.commit()
    
    return jsonify(updated_tasks)

# ==========================================================
# Funciones Helper
# ==========================================================

def _update_search_details(search_obj, result_dict):
    """Actualiza un objeto Search con los datos del resultado del análisis."""
    if not result_dict:
        return

    search_obj.status = 'done' if result_dict.get('status') == 'ok' else 'error'
    search_obj.title = result_dict.get('title')
    search_obj.description = result_dict.get('description')
    search_obj.loading_time = result_dict.get('time')
    search_obj.hosting_company = result_dict.get('hosting_company')
    
    # Guardamos el resto de la información en el campo JSONB
    details = {
        'dns_info': result_dict.get('dns_info'),
        'domain_registry': result_dict.get('domain_registry'),
        'nameservers': result_dict.get('nameservers'),
        'email_services': result_dict.get('email_services')
    }
    search_obj.details = details

# -------------------------- TCP Helpers --------------------------

def enviar_url_al_servidor(url):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('analyzer_service', 9999))
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
            sock.connect(('analyzer_service', 9999))
            request_data = { "action": "consultar", "task_id": task_id }
            sock.sendall(json.dumps(request_data).encode())
            response = sock.recv(4096)
            return json.loads(response.decode())
    except (socket.error, json.JSONDecodeError, ConnectionRefusedError) as e:
        print(f"Error en consultar_resultado: {e}")
        return None

@app.cli.command('init-db')
def init_db_command():
    """Crea las tablas de la base de datos."""
    db.create_all()
    print('Base de datos inicializada.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)