# 🌐 WebAnalyzer Pro

**WebAnalyzer Pro** es un sistema distribuido para el análisis técnico de sitios web. Está diseñado como proyecto final para la materia **Computación II** de Ingeniería en Informática, e integra múltiples tecnologías y conceptos vistos en clase: sockets, concurrencia, asincronismo, IPC, multiproceso, scraping, y contenedores.

El sistema permite a usuarios conectarse por socket TCP, enviar una URL a analizar, y luego consultar el resultado por un `task_id`. Todo el análisis se realiza en segundo plano con asincronismo real (`asyncio`), y se está integrando un **módulo de autenticación separado por IPC** y una **interfaz web con historial personal**.

---

## 🎯 Objetivos académicos cumplidos

- ✅ Conexión de múltiples clientes concurrentes (socket TCP + threads)
- ✅ Uso de asincronismo para tareas I/O-bound (`asyncio.create_task`)
- ✅ Comunicación entre procesos (IPC) para autenticación de usuarios
- ✅ Parseo de argumentos por línea de comandos en scripts cliente
- ✅ Arquitectura modular extensible
- 🐳 Despliegue en contenedores Docker (en curso)
- 🌐 Interfaz web para login y visualización de historial (en curso)
- 💾 Almacenamiento de tareas por usuario (en curso)

---

## 🧠 Funcionalidades actuales

- 🚪 Servidor TCP multicliente (`ThreadingMixIn`)
- ⚡ Tareas asíncronas en segundo plano (`aiohttp`, `asyncio`)
- 🔁 Consulta de resultados por `task_id`
- 🧹 Web scraping básico: título, descripción, tiempo de carga
- 💬 Protocolo de mensajes JSON
- 📡 Cliente CLI (`client.py`) y verificador (`check_result.py`)

---

## 🧱 En desarrollo / Próximas funcionalidades

| Funcionalidad                  | Tecnología |
|-------------------------------|------------|
| 🔐 Autenticación por IPC       | `multiprocessing.Process` + `Pipe` / `Queue`  
| 🌐 Interfaz web                | `Flask`, `Bootstrap`, `SQLite`
| 📬 Historial personal          | Asociación usuario ↔ task_id ↔ resultados
| 🌎 DNS Lookup async            | `aiodns`
| 🕵️ WHOIS asincrónico           | `asyncio.create_subprocess_exec()`
| 🐳 Dockerización               | `docker-compose` con servicios: server, auth, web, redis (opcional)
| 📂 Almacenamiento persistente | `SQLite` (simple) o `PostgreSQL` (para escalar)
| 🖼️ UI visual                   | Resultados graficados en web con métricas

---

## 📁 Estructura del proyecto

```
final/
├── server.py                # Servidor TCP multicliente asincrónico
├── client.py                # Cliente CLI para enviar solicitudes de análisis
├── check_result.py          # Cliente CLI para consultar resultados por task_id
├── analyzer_async.py        # Scraping y análisis con aiohttp
├── auth_process.py          # Proceso separado para autenticar usuarios (IPC)
├── web/
│   ├── app.py               # Panel web Flask
│   ├── templates/
│   └── static/
├── database/
│   └── models.py            # Usuarios, tareas, resultados
├── docker-compose.yml       # Orquestación de contenedores
├── Dockerfile               # Imagen del servidor
├── requirements.txt         # Dependencias
└── README.md
```

---

## 🚀 Cómo ejecutar

### 1. Instalar dependencias
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar el servidor TCP
```bash
python server.py
```

### 3. Enviar una URL
```bash
python client.py --url https://ejemplo.com
```

### 4. Consultar el estado o resultado
```bash
python check_result.py --task-id 123e4567-e89b-12d3-a456-426614174000
```

---

## 💻 Interfaz web (próximamente)

- Pantalla de login
- Panel con historial personal
- Estado de cada análisis
- Detalles visuales del resultado (carga, título, descripción, etc.)
- Exportación a JSON o CSV

---

## 🧪 Análisis técnico actual (Scraping)

| Elemento                 | ¿Qué se analiza?                            |
|--------------------------|---------------------------------------------|
| ✅ Título (`<title>`)     | Extraído con BeautifulSoup                 |
| ✅ Meta descripción       | Tag `<meta name="description">`            |
| ✅ Tiempo de respuesta    | Medido con `time.time()` y `aiohttp`       |
| (en curso) DNS            | Consulta asincrónica con `aiodns`          |
| (en curso) WHOIS          | Ejecutado como subprocess                  |
| (planificado) CMS detectado | WordPress, Shopify, etc. (por HTML hints) |

---

## 🐳 Docker & Despliegue (en construcción)

```bash
docker-compose up --build
```

Servicios planeados:
- `server`: contenedor del servidor TCP
- `auth`: proceso autenticador (IPC)
- `web`: frontend Flask
- `db`: SQLite o PostgreSQL
- `redis` (opcional): si se extiende a tareas Celery en futuro

---

## 📜 Ejemplo de análisis exitoso

```json
{
  "status": "done",
  "task_id": "4b58a52a-bda9-4d0b-a87a-dfb1225e3915",
  "result": {
    "url": "https://www.python.org",
    "title": "Welcome to Python.org",
    "description": "The official home of the Python Programming Language.",
    "time": 1.36
  }
}
```

---

## 👨‍🎓 Créditos

Proyecto desarrollado por **Franco Zapata**  
Ingeniería en Informática – Universidad de Mendoza  
Materia: **Computación II**

---

## 📝 Licencia

Uso educativo y académico. Para uso comercial, contactar al autor.