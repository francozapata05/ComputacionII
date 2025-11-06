def analizar_rendimiento(driver):
    """Analiza el rendimiento de la página usando la Navigation Timing API del navegador."""
    print("[Procesamiento] Analizando rendimiento...")
    try:
        # Ejecutar script para obtener las métricas de performance.timing
        # Estas métricas están en milisegundos desde el epoch.
        performance_script = """
        return window.performance.timing.toJSON();
        """
        timing = driver.execute_script(performance_script)

        # Calcular duraciones en milisegundos
        # Si una métrica es 0, significa que el evento no ocurrió o no aplica.
        if not timing or timing.get('loadEventEnd') == 0:
            # Si la página no terminó de cargar, no podemos calcular métricas fiables
            return {"error": "La página no completó su evento de carga."}

        # Tiempo total de carga de la página
        load_time_ms = timing['loadEventEnd'] - timing['navigationStart']
        # Tiempo de resolución de DNS
        dns_lookup_ms = timing['domainLookupEnd'] - timing['domainLookupStart']
        # Tiempo de conexión TCP
        connection_time_ms = timing['connectEnd'] - timing['connectStart']
        # Tiempo hasta el primer byte (TTFB)
        ttfb_ms = timing['responseStart'] - timing['navigationStart']
        # Tiempo de descarga del contenido
        content_download_ms = timing['responseEnd'] - timing['responseStart']
        # Tiempo de procesamiento del DOM
        dom_processing_ms = timing['domComplete'] - timing['domInteractive']

        print("[Procesamiento] Análisis de rendimiento completado.")
        return {
            "load_time_ms": load_time_ms,
            "dns_lookup_ms": dns_lookup_ms,
            "connection_time_ms": connection_time_ms,
            "time_to_first_byte_ms": ttfb_ms,
            "content_download_ms": content_download_ms,
            "dom_processing_ms": dom_processing_ms
        }

    except Exception as e:
        print(f"[Procesamiento] Error al analizar rendimiento: {e}")
        return {"error": str(e)}
