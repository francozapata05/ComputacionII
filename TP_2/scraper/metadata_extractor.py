from bs4 import BeautifulSoup

def extract_meta_tags(content):
    """Extrae meta tags relevantes del contenido HTML."""
    soup = BeautifulSoup(content, 'html.parser')
    meta_tags_deseadas = ["description", "keywords", "og:title"]
    meta_tags_encontradas = {
        meta.get('name', meta.get('property', '')): meta.get('content', '') 
        for meta in soup.find_all('meta')
    }
    meta_tags_filtradas = {k: meta_tags_encontradas.get(k, '...') for k in meta_tags_deseadas}
    return meta_tags_filtradas
