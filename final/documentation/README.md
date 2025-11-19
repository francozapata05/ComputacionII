# 🌐 WebAnalyzer Pro

**WebAnalyzer Pro** es un sistema distribuido para el análisis técnico de sitios web, completamente funcional y contenerizado. Fue desarrollado como proyecto final para la materia **Computación II** de Ingeniería en Informática, integrando tecnologías como sockets, concurrencia, asincronismo, IPC, multiproceso, scraping y contenedores.

El sistema permite a los usuarios registrarse, iniciar sesión y, a través de una interfaz web, enviar URLs para su análisis. Los resultados se almacenan y se muestran en un historial personal. La arquitectura se basa en microservicios que se comunican por TCP, orquestados con Docker Compose.

---

## 🎯 Objetivos académicos cumplidos

- ✅ **Concurrencia:** Conexión de múltiples clientes a través de una aplicación web.
- ✅ **Asincronismo:** Uso de `asyncio` para tareas de análisis I/O-bound en un servicio dedicado.
- ✅ **Comunicación entre procesos (IPC):** Múltiples servicios (`web`, `auth_service`, `analyzer_service`) comunicándose a través de sockets TCP dentro de una red Docker, y un sistema de logging desacoplado usando `multiprocessing.Queue`.
- ✅ **Arquitectura de Microservicios:** El sistema está desacoplado en servicios independientes para la web, autenticación y análisis.
- ✅ **Contenerización:** Despliegue completo y orquestado con `docker-compose`.
- ✅ **Interfaz Web:** Interfaz de usuario funcional con Flask para registro, login, dashboard e historial.
- ✅ **Almacenamiento Persistente:** Uso de PostgreSQL para almacenar usuarios y resultados de análisis.

---

## 🧠 Funcionalidades implementadas

- 🔐 **Autenticación de Usuarios:** Registro e inicio de sesión seguros.
- 👤 **Sesiones de Usuario:** Gestión de sesiones para una experiencia personalizada.
- 🌐 **Interfaz Web Completa:** Un panel de control (`dashboard`) para enviar URLs y ver el historial de análisis.
- ⚡ **Análisis Asíncrono:** Las tareas de análisis se ejecutan en segundo plano sin bloquear la interfaz de usuario.
- 💾 **Base de Datos Robusta:** PostgreSQL para persistencia de datos de usuarios y análisis.
- 🐳 **Orquestación con Docker:** Todos los servicios están definidos y gestionados con `docker-compose`.
- 📡 **Comunicación por Sockets TCP:** Los servicios internos se comunican a través de la red de Docker.
- ⚙️ **Soporte Dual-Stack (IPv4/IPv6):** El servidor de análisis es accesible desde redes IPv4 e IPv6, garantizando compatibilidad y robustez.
- 📝 **Logging Desacoplado:** Registro de todas las tareas de análisis en un archivo local (`analysis.log`) mediante un proceso dedicado para no impactar el rendimiento.

---

## 🧱 Próximas funcionalidades (Sugerencias)

| Funcionalidad Potencial        | Tecnología Sugerida        |
|--------------------------------|----------------------------|
| 📊 Visualización de Métricas   | `Chart.js` o `D3.js`       |
| 🔄 Análisis Periódico          | Tareas programadas (`Celery Beat`) |
| 📤 Exportación de Resultados   | Generación de CSV o PDF    |
| 🎨 Mejoras en la UI/UX          | Frameworks de CSS más avanzados |
| 🧪 Más Métricas de Análisis     | `Lighthouse`, `Selenium`   |

---

## 📁 Estructura del proyecto

```
final/
├── app/
│   ├── app.py               # Aplicación web principal (Flask)
│   ├── auth_client.py       # Cliente para el servicio de autenticación
│   ├── templates/           # Plantillas HTML para la interfaz web
│   └── static/              # Archivos estáticos (CSS, JS)
├── database/
│   └── models.py            # Modelos de datos SQLAlchemy (User, Search)
├── auth_process.py          # Servicio de autenticación
├── server.py                # Servidor de análisis (analyzer_service)
├── analyzer_async.py        # Lógica de scraping y análisis con aiohttp
├── log_process.py           # Proceso dedicado para la escritura de logs
├── analysis.log             # Archivo de logs de análisis
├── docker-compose.yml       # Orquestación de todos los servicios
├── Dockerfile               # Define la imagen para los servicios
├── requirements.txt         # Dependencias de Python
└── README.md
```

---

## 🔌 Arquitectura de Red y Logging

### Soporte Dual-Stack (IPv4/IPv6)

Para maximizar la compatibilidad y preparar el sistema para el futuro de internet, el servidor de análisis (`server.py`) implementa una arquitectura "Dual-Stack".

- **Detección Automática:** Al iniciar, el servidor detecta todas las interfaces de red disponibles.
- **Servidores Dedicados:** Lanza un servidor de escucha independiente para cada familia de protocolos encontrada (uno para `AF_INET` - IPv4 y otro para `AF_INET6` - IPv6).
- **Aislamiento de Sockets:** Se utiliza la opción `IPV6_V6ONLY` en el socket IPv6 para evitar conflictos de puertos, permitiendo que ambos servidores coexistan sin problemas.

Esto garantiza que cualquier cliente, sin importar si su red es solo IPv4, solo IPv6, o dual, pueda conectarse y utilizar el servicio de análisis.

### Sistema de Logging

Se ha implementado un sistema de logging asíncrono y desacoplado para registrar todas las operaciones de análisis sin afectar el rendimiento del servidor principal.

- **Proceso Dedicado:** Un proceso completamente separado (`log_process.py`) se encarga de toda la escritura en disco.
- **Comunicación por Cola (IPC):** Los hilos del servidor de análisis no escriben directamente en el archivo. En su lugar, colocan mensajes de log en una `multiprocessing.Queue`. Esta es una operación extremadamente rápida y no bloqueante.
- **Archivo de Log:** El proceso logger lee los mensajes de la cola y los escribe en `analysis.log` en formato JSON, donde cada línea es un registro.

**Ejemplo de entrada en `analysis.log`:**
```json
{"timestamp": "2025-11-18T15:45:10.123456", "source": "analyzer", "event": "analysis_started", "url": "google.com"}
```

---

## 🚀 Cómo ejecutar

### 1. Prerrequisitos
- Tener `Docker` y `docker-compose` instalados.

### 2. Configuración
- Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
  ```
  POSTGRES_USER=tu_usuario
  POSTGRES_PASSWORD=tu_contraseña
  POSTGRES_DB=tu_base_de_datos
  FLASK_SECRET_KEY=una_clave_secreta_muy_segura
  ```

### 3. Iniciar la aplicación
- Abre una terminal en la raíz del proyecto y ejecuta:
  ```bash
  docker-compose up --build -d
  ```
- La aplicación web estará disponible en `http://localhost:5000`.

### 4. Detener la aplicación
```bash
docker-compose down
```
Para eliminar la base de datos junto con los contenedores (por ejemplo, después de un cambio en el modelo de datos), usa:
```bash
docker-compose down -v
```

---

## 💻 Interfaz web

- **/register**: Página para crear una nueva cuenta de usuario.
- **/login**: Página para iniciar sesión.
- **/dashboard**: Panel principal donde se pueden enviar URLs para analizar y ver el historial de análisis.
- **/logout**: Cierra la sesión del usuario.

---

## 🧪 Análisis técnico actual

| Elemento                 | ¿Qué se analiza?                            |
|--------------------------|---------------------------------------------|
| ✅ Título (`<title>`)     | Extraído con BeautifulSoup                 |
| ✅ Meta descripción       | Tag `<meta name="description">`            |
| ✅ Tiempo de respuesta    | Medido con `time.time()` y `aiohttp`       |
| ✅ DNS (IPs)              | Resuelve los IPs asociados al hostname     |
| ✅ Hosting                | Identifica la organización de hosting (vía IP) |
| ✅ Registros NS y MX      | Obtiene los servidores de nombres y de correo |
| ✅ WHOIS                  | Información del registrador del dominio    |

---

## 🐳 Docker & Despliegue

La aplicación está completamente orquestada con `docker-compose`. Los servicios definidos son:

- `db`: Contenedor con la base de datos PostgreSQL.
- `auth_service`: Servicio que maneja la lógica de autenticación.
- `analyzer_service`: Servicio que procesa las solicitudes de análisis de URLs.
- `web`: La aplicación Flask que sirve la interfaz de usuario.
- `log_process`: Proceso en segundo plano que gestiona la escritura de logs.

Todos los servicios se comunican entre sí a través de una red interna de Docker.

---

## 📜 Ejemplo de análisis exitoso (en la web)

Una vez que un análisis se completa, se muestra en el historial del dashboard con su título, descripción y tiempo de carga.

---

## 👨‍🎓 Créditos

Proyecto desarrollado por **Franco Zapata**  
Ingeniería en Informática – Universidad de Mendoza  
Materia: **Computación II**

---

## 📝 Licencia

Uso educativo y académico. Para uso comercial, contactar al autor.