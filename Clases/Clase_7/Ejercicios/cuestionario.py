import signal

# Handler para SIGALRM
def timeout_handler(signum, frame):
    print("\n⏰ ¡Tiempo agotado!")
    raise TimeoutError

# Asociar el handler a SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

try:
    print("📘 Pregunta: ¿Cuál es la capital de Francia?")
    print("⏳ Tenés 5 segundos para responder...")

    signal.alarm(5)  # Dispara SIGALRM en 5 segundos

    respuesta = input("👉 Tu respuesta: ")
    
    signal.alarm(0)  # Cancela la alarma si respondiste a tiempo

    if respuesta.strip().lower() == "parís" or respuesta.strip().lower() == "paris":
        print("✅ ¡Correcto!")
    else:
        print("❌ Incorrecto. La respuesta era: París")

except TimeoutError:
    print("❌ No respondiste a tiempo.")

