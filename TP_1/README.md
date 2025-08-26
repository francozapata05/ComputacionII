# 🩺 Simulador de Monitoreo de Pacientes con Blockchain
Este proyecto, desarrollado para la materia Computación II, simula un sistema de monitoreo de signos vitales de pacientes en tiempo real. Los datos generados son procesados de forma concurrente y almacenados de manera segura e inmutable en una cadena de bloques (blockchain).

## 📝 Descripción General
El sistema utiliza múltiples procesos que se comunican entre sí para realizar distintas tareas:

Generación de Datos: Un proceso simula la llegada de datos de un paciente (frecuencia cardíaca, presión arterial, saturación de oxígeno).

Análisis de Datos: Tres procesos analizadores reciben estos datos en paralelo. Cada uno se especializa en un signo vital y calcula estadísticas de media y desviación estándar sobre una ventana de tiempo móvil.

Construcción de la Blockchain: Un proceso verificador recopila los datos analizados, los consolida, determina si representan una alerta médica y los sella en un nuevo bloque que se añade a la cadena.

Verificación y Reporte: Al finalizar la simulación, se verifica la integridad de toda la cadena de bloques recalculando los hashes y se genera un reporte final con estadísticas agregadas.

## 🏗️ Arquitectura del Sistema
El sistema está diseñado con una arquitectura de procesos concurrentes que se comunican a través de FIFOs (Named Pipes) y Queues.

El flujo de datos es el siguiente:

El Proceso Generador crea datos de signos vitales y los escribe simultáneamente en tres FIFOs.

Cada uno de los tres Procesos Analizadores lee de su FIFO asignado.

Los Analizadores procesan los datos y envían los resultados (estadísticas) a través de Queues al proceso verificador.

El Proceso Verificador lee de las tres Queues, ensambla los datos en un bloque, calcula su hash y lo escribe en el archivo blockchain.json.

Finalmente, el script verificar_cadena.py lee el archivo blockchain.json para validar la cadena y generar un reporte.

## 🛠️ Componentes y Scripts
El proyecto está dividido en los siguientes módulos:

main.py: Orquesta la creación de todos los procesos, canales de comunicación (FIFOs, Queues) y eventos de sincronización. Inicia la simulación y, al finalizar, ejecuta la verificación y el reporte.

generador.py: Simula un dispositivo médico que genera datos de pacientes a intervalos regulares.

analizador_a.py, analizador_b.py, analizador_c.py: Cada uno lee un tipo de dato (frecuencia, presión, oxígeno) y lo procesa.

VentanaMovil.py: Clase auxiliar utilizada por los analizadores para calcular estadísticas (media, desviación) sobre una ventana de tiempo deslizante de 30 segundos.

verificador.py: Recibe los datos procesados, los organiza en bloques, calcula el hash criptográfico (SHA-256) y construye la blockchain, guardándola en blockchain.json.

verificar_cadena.py: Contiene la lógica para:

Verificar la integridad de la blockchain recalculando cada hash.

Generar un reporte final en reporte.txt con estadísticas de la simulación.

fifos.py: Utilidad para crear los named pipes (FIFOs) necesarios para la comunicación entre el generador y los analizadores.

## Librerías Principales:

multiprocessing: Para la gestión de procesos (Process), comunicación (Queue) y sincronización (Event).

os: Para la creación y manejo de FIFOs.

json: Para la serialización y deserialización de datos.

hashlib: Para la generación de hashes criptográficos SHA-256, pilar de la blockchain.

## ⚙️ Cómo Ejecutar el Programa
Asegúrate de tener Python 3 instalado.

Coloca todos los archivos .py en el mismo directorio.

Abre una terminal en ese directorio y ejecuta el siguiente comando:

python3 main.py

El programa comenzará a ejecutarse, mostrando en la terminal los mensajes de cada proceso a medida que generan, analizan y verifican los datos.

### 📄 Archivos Generados
Al finalizar la ejecución, se habrán creado (o actualizado) los siguientes archivos en el directorio /tmp/:

/tmp/blockchain.json: Un archivo JSON que contiene la lista de todos los bloques generados, formando la cadena de bloques completa.

/tmp/reporte.txt: Un archivo de texto con un resumen de la simulación, incluyendo la cantidad total de bloques, el número de alertas detectadas y las medias generales de los signos vitales.

/tmp/fifo_a, /tmp/fifo_b, /tmp/fifo_c: Los named pipes utilizados para la comunicación, que son eliminados y recreados al inicio de cada ejecución.
