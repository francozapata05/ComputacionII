import json, hashlib, os

BLOCKCHAIN_PATH = "/tmp/blockchain.json"
REPORT_PATH = "/tmp/reporte.txt"

def calcular_hash(prev_hash, datos, timestamp):
    """
    Genera hash SHA-256 de forma consistente con la función del verificador.
    """
    cadena = f"{prev_hash}{json.dumps(datos, sort_keys=True)}{timestamp}"
    return hashlib.sha256(cadena.encode()).hexdigest()

def recalcular_hash(bloque):

    try:
        timestamp_usado = bloque['timestamp']
    except KeyError:
        print(f"Advertencia de verificación: Bloque no contiene clave 'timestamp'.")
        return True 

    hash_recalculado = calcular_hash(
        bloque['prev_hash'],
        bloque['datos'],
        timestamp_usado
    )
    
    return bloque['hash'] != hash_recalculado

def verificar_cadena():

    lista_corruptos = []

    try:
        with open(BLOCKCHAIN_PATH, "r") as f:
            blockchain = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {BLOCKCHAIN_PATH}.")
        return lista_corruptos
    except Exception as e:
        print(f"Verificador Blockchain Error Cargar Blockchain: {e}")
        return lista_corruptos

    if len(blockchain) < 1:
        print("Error: Blockchain vacía")
        return lista_corruptos
    
    for index in range(len(blockchain)):
        bloque = blockchain[index]
        
        # Recalcula el hash del bloque actual y verifica si es diferente al guardado
        if recalcular_hash(bloque):
            lista_corruptos.append(f"Bloque {index} (Hash Propio Corrupto)")
            
        # Verificar el encadenamiento (a partir del bloque 1)
        if index > 0:
            bloque_anterior = blockchain[index - 1]
            # Comprueba si el prev_hash del bloque actual coincide con el hash del anterior
            if bloque.get('prev_hash') != bloque_anterior.get('hash'):
                # Usamos .get() para evitar KeyError si la estructura del bloque es inconsistente
                lista_corruptos.append(f"Bloque {index} (Encadenamiento Roto)")

    return lista_corruptos

def reporte_final():
    
    try:
        with open(BLOCKCHAIN_PATH, "r") as f:
            blockchain = json.load(f)
    except Exception as e:
        print(f"Verificador Blockchain Error Cargar Blockchain: {e}")
        return
        
    cant_total_bloques = len(blockchain)
    cant_bloques_datos = cant_total_bloques - 1 # Bloques con datos (omitiendo el Génesis)

    # Si solo está el Génesis, no hay datos para promediar
    if cant_bloques_datos <= 0:
        print("\nReporte: Solo existe el bloque Génesis. No hay datos para promediar.")
        return

    alertas = 0
    frecuencias_sum = 0
    presiones_sum = 0
    oxigenos_sum = 0

    # El bucle empieza en 1 para ignorar el Bloque Génesis (índice 0)
    for index in range(1, cant_total_bloques):
        bloque = blockchain[index]
        
        if bloque.get('alerta', False) == True: # Usamos .get() con fallback por seguridad
            alertas += 1
            
        try:
            frecuencias_sum += bloque['datos']['frecuencia']['media']
            presiones_sum += bloque['datos']['presion']['media']
            oxigenos_sum += bloque['datos']['oxigeno']['media']
        except KeyError as e:
            print(f"Advertencia: Bloque {index} incompleto o corrupto (falta clave {e}). Saltando suma de datos.")


    # CÁLCULO DE PROMEDIOS CORREGIDO
    frecuencia_media = frecuencias_sum / cant_bloques_datos
    presion_media = presiones_sum / cant_bloques_datos
    oxigeno_media = oxigenos_sum / cant_bloques_datos

    # Generar y mostrar reporte
    try:
        with open(REPORT_PATH, "w") as f:
            f.write(f"Cantidad Total de Bloques (incl. Génesis): {cant_total_bloques}\n")
            f.write(f"Cantidad de Bloques con Datos: {cant_bloques_datos}\n")
            f.write(f"Cantidad Alertas: {alertas}\n")
            f.write(f"Frecuencia Media General: {frecuencia_media:.2f}\n")
            f.write(f"Presion Media General: {presion_media:.2f}\n")
            f.write(f"Oxigeno Media General: {oxigeno_media:.2f}\n")
    except Exception as e:
        print(f"Verificador Blockchain Error Reporte: {e}")

    # Mostrar el reporte en la consola
    print(f"\n--- REPORTE FINAL ({REPORT_PATH}) ---")
    os.system(f"cat {REPORT_PATH}")
    print("-------------------------------------")


if __name__ == '__main__':
    lista_corruptos = verificar_cadena()
    if lista_corruptos:
        print(f"\n¡ADVERTENCIA! Se encontraron bloques corruptos: {lista_corruptos}")
    else:
        print("\nVerificación de integridad exitosa. No se encontraron bloques corruptos.")
        
    print("Verificador Blockchain: Terminado")
    reporte_final()
