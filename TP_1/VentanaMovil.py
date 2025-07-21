import time, json, math

class VentanaMovil:
    def __init__(self, tiempo=30):
        self.datos = [] # Tuplas (timestamp, valor)
        self.ventana = tiempo

    def agregar(self, valor, timestamp):
        if isinstance(valor, list):
            sistolica = valor[0]
            self.datos.append((timestamp, sistolica))
        else:
            self.datos.append((timestamp, valor))
        self._limpiar()
    
    def _limpiar(self):
        ahora = time.time()
        # Filtrado seguro con comprensión de listas
        i = 0
        for timestamp, val in self.datos:
            if (ahora - timestamp) >= self.ventana:
                self.datos.pop(i)
                i =+ 1
    
    def obtener_datos(self):
        self._limpiar()
        return [val for (_, val) in self.datos]
    
    def promedio(self):
        datos = self.obtener_datos()  # Lista de valores
        return sum(datos)/len(datos)
    
    def desviacion(self):
        datos = self.obtener_datos()
        if len(datos) < 2:
            return 0
        promedio = self.promedio()
        suma_cuadrados = sum((x - promedio) ** 2 for x in datos)
        return math.sqrt(suma_cuadrados / (len(datos) - 1))  # Desviación muestral
    
    def formatear_datos(self, tipo, timestamp):
        datos = {
            "tipo": tipo,
            "timestamp": timestamp,
            "media": self.promedio(),
            "desv": self.desviacion()
        }
        return json.dumps(datos).encode()