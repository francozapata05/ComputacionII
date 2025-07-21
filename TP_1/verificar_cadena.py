import json, hashlib, os

def verificar_cadena():
    blockchain_path = "/tmp/blockchain.json"    
    lista_corruptos = []

    try:
        with open(blockchain_path, "r") as f:
            blockchain = json.load(f)
    except Exception as e:
        print(f"Verificador Blockchain Error Cargar Blockchain: {e}")
        return lista_corruptos

    if not blockchain:
        print("Error: Blockchain vacía")
        return False

    for index in range(len(blockchain)):
        bloque = blockchain[index]
        if recalcular_hash(bloque, index):
            lista_corruptos.append(index)
    return lista_corruptos

        
def recalcular_hash(bloque, index):
    if index == 0:
        timestamp = bloque['datos']['timestamp']
    else:
        timestamp = bloque['timestamp']
    cadena = f"{bloque['prev_hash']}{json.dumps(bloque['datos'], sort_keys=True)}{timestamp}"
    hash_recalculado = hashlib.sha256(cadena.encode()).hexdigest()
    
    if bloque['hash'] != hash_recalculado:
        return True
    return False

def reporte_final():
    blockchain_path = "/tmp/blockchain.json"
    try:
        with open(blockchain_path, "r") as f:
            blockchain = json.load(f)
    except Exception as e:
        print(f"Verificador Blockchain Error Cargar Blockchain: {e}")
        
    cant_bloques = len(blockchain)
    alertas = 0
    frecuencias = 0
    presiones = 0
    oxigenos = 0


    for index in range(1,cant_bloques):
        bloque = blockchain[index]
        if bloque['alerta'] == True:
            alertas += 1
        frecuencias += bloque['datos']['frecuencia']['media']
        presiones += bloque['datos']['presion']['media']
        oxigenos += bloque['datos']['oxigeno']['media']

    frecuencia_media = frecuencias / cant_bloques
    presion_media = presiones / cant_bloques
    oxigeno_media = oxigenos / cant_bloques

    reporte_path = "/tmp/reporte.txt"
    try:
        with open(reporte_path, "w") as f:
            f.write(f"Cantidad Total de Bloques: {(cant_bloques)}\n")
            f.write(f"Cantidad Alertas: {alertas}\n")
            f.write(f"Frecuencia Media: {frecuencia_media}\n")
            f.write(f"Presion Media: {presion_media}\n")
            f.write(f"Oxigeno Media: {oxigeno_media}\n")
    except Exception as e:
        print(f"Verificador Blockchain Error Reporte: {e}")

    os.system(f"cat {reporte_path}")

if __name__ == '__main__':
    lista_corruptos = verificar_cadena()
    print(f"Lista de bloques corruptos: {lista_corruptos}")
    print("Verificador Blockchain: Terminado")
    reporte_final()