# En el futuro se conectará por Pipe a auth_process.py
def autenticar_usuario(usuario, clave):
    # Simulamos autenticación válida si el usuario es 'admin' y clave '1234'
    return usuario == 'admin' and clave == '1234'
