import os


def generar_screenshot(driver, output_dir):
    """Toma una captura de pantalla desde una instancia de driver ya navegada y la guarda en disco. Devuelve la ruta del archivo."""
    print("[Procesamiento] Generando screenshot...")
    try:
        # Asegurarse de que el directorio de salida exista
        os.makedirs(output_dir, exist_ok=True)
        screenshot_filename = os.path.join(output_dir, "screenshot.png")
        driver.save_screenshot(screenshot_filename)
        print(f"[Procesamiento] Screenshot guardado exitosamente en: {screenshot_filename}")
        return screenshot_filename
    except Exception as e:
        print(f"[Procesamiento] Error al generar screenshot: {e}")
        return None
