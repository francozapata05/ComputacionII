from bs4 import BeautifulSoup
from collections import Counter

def parse_html_content(content):
    """Parsea el contenido HTML y extrae información básica."""
    soup = BeautifulSoup(content, 'html.parser')
    
    titulo = soup.title.string if soup.title else ''
    enlaces = [a.get('href') for a in soup.find_all('a', href=True)]
    cantidad_de_imagenes = len(soup.find_all('img'))
    image_urls = [img.get('src') for img in soup.find_all('img', src=True)]
    cabeceras = [h.name for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    estructura_conteo = dict(Counter(cabeceras))

    return {
        "titulo": titulo,
        "enlaces": enlaces,
        "cantidad_de_imagenes": cantidad_de_imagenes,
        "image_urls": image_urls,
        "estructura_conteo": estructura_conteo
    }
