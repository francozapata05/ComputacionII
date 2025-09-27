import json, datetime, hashlib

def extraer_datos_paciente(queues):
    datos = {}
    try:
        # Extraemos datos de cada Queue
        frecuencia_json = queues[0].get()
        presion_json = queues[1].get()
        oxigeno_json = queues[2].get()
    except Exception as e:
        print(f"Verificador Error Extraer Queues: {e}")
    
    # Les damos el formato json apropiado, falta Alerta y Hashs
    datos = {
        "frecuencia":{
            "media": json.loads(frecuencia_json)["media"],
            "desv": json.loads(frecuencia_json)["desv"]
        },
        "presion":{
            "media": json.loads(presion_json)["media"],
            "desv": json.loads(presion_json)["desv"]
        },
        "oxigeno":{
            "media": json.loads(oxigeno_json)["media"],
            "desv": json.loads(oxigeno_json)["desv"]
        }
    }
    
    return datos
    

def construir_bloque(datos, alerta, prev_hash):
    # Construimos el bloque con los datos y el hash previo
    bloque = {
        "timestamp": datetime.datetime.now().timestamp(),
        "datos": datos,
        "alerta": alerta,
        "prev_hash": prev_hash,
        "hash": None # Dejamos en none, porque usamos los datos del bloque para hash
    }
    # Calculamos el hash del bloque
    bloque["hash"] = calcular_hash(
        bloque["prev_hash"], 
        bloque["datos"], 
        bloque["timestamp"])
    return bloque

def calcular_hash(prev_hash, datos, timestamp):
    # Genera hash SHA-256 apartir de concatenacion prevhash, datos y timestamp
    cadena = f"{prev_hash}{json.dumps(datos, sort_keys=True)}{timestamp}"
    return hashlib.sha256(cadena.encode()).hexdigest()

def inicializar_blockchain(blockchain_path, blockchain):
    """
    Inicializa el archivo blockchain:
    - Si no existe, lo crea con bloque génesis
    - Si existe, lo sobrescribe con bloque génesis (limpia contenido previo)
    """
    # Estructura del bloque génesis
    bloque_genesis = {
        "datos" : {
            "timestamp": datetime.datetime.now().timestamp(),
            "mensaje": "Bloque Génesis",
        },
        "prev_hash": "0"*64,  # 64 ceros como hash previo inicial
        "hash": None
    }
    bloque_genesis["hash"] = calcular_hash(
        bloque_genesis["prev_hash"], 
        bloque_genesis["datos"], 
        bloque_genesis['datos']['timestamp']
    )

    blockchain.append(bloque_genesis)
    
    # Siempre escribimos el bloque génesis (sobreescribiendo si existe)
    with open(blockchain_path, 'w') as f:
        json.dump([bloque_genesis], f, indent=2)
    
    print(f"Archivo {blockchain_path} inicializado con bloque génesis\n")
    print(f"Bloque 0: {bloque_genesis}\n")


def verificador(i, queues):
    # Asignaremos los bloques a una lista para acceder al prev_hash
    blockchain = []

    blockchain_path = "/tmp/blockchain.json"
    inicializar_blockchain(blockchain_path, blockchain)

    try:
        for i in range(60):
            # Extraer datos de cada Queue
            datos = extraer_datos_paciente(queues)

            # Accedemos a las Medias
            frecuencia_media = datos["frecuencia"]["media"]
            presion_media = datos["presion"]["media"]
            oxigeno_media = datos["oxigeno"]["media"]
            alerta = False 
            
            if not (frecuencia_media < 200):
                alerta = True
            
            if not (presion_media < 200):
                alerta = True

            if not (90 <= oxigeno_media <= 100):
                alerta = True

            nuevo_bloque = construir_bloque(datos, alerta, blockchain[-1]["hash"])
            blockchain.append(nuevo_bloque)   

            print(f"Bloque {i + 1}: {nuevo_bloque}\n")
            
            try:
                # Guardar en blockchain.json
                with open(blockchain_path, "w") as f:
                    json.dump(blockchain, f, indent=2)
            except Exception as e:
                print(f"Verificador Error Guardar Blockchain: {e}")

    except Exception as e:
        print(f"Error Verificador: {e}")



