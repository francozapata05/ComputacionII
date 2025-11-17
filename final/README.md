# 🌐 WebAnalyzer Pro

**WebAnalyzer Pro** es un sistema distribuido para el análisis técnico de sitios web, completamente funcional y contenerizado. Fue desarrollado como proyecto final para la materia **Computación II** de Ingeniería en Informática, integrando tecnologías como sockets, concurrencia, asincronismo, IPC, multiproceso, scraping y contenedores.

El sistema permite a los usuarios registrarse, iniciar sesión y, a través de una interfaz web, enviar URLs para su análisis. Los resultados se almacenan y se muestran en un historial personal. La arquitectura se basa en microservicios que se comunican por TCP, orquestados con Docker Compose.

---

## 🎯 Objetivos académicos cumplidos

- ✅ **Concurrencia:** Conexión de múltiples clientes a través de una aplicación web.
- ✅ **Asincronismo:** Uso de `asyncio` para tareas de análisis I/O-bound en un servicio dedicado.
- ✅ **Comunicación entre procesos (IPC):** Múltiples servicios (`web`, `auth_service`, `analyzer_service`) comunicándose a través de sockets TCP dentro de una red Docker.
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
├── docker-compose.yml       # Orquestación de todos los servicios
├── Dockerfile               # Define la imagen para los servicios
├── requirements.txt         # Dependencias de Python
└── README.md
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