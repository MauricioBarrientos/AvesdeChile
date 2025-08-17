import requests
from jinja2 import Environment, FileSystemLoader
import time
import json
import os

# Función para obtener datos de la API
def fetch_birds_data():
    url = 'https://aves.ninjas.cl/api/birds'
    response = requests.get(url)
    response.raise_for_status()  # Levantar una excepción si la respuesta contiene un error
    birds_data = response.json()
    
    # Guardar los datos en un archivo JSON para uso futuro
    with open('birds_data.json', 'w', encoding='utf-8') as f:
        json.dump(birds_data, f, ensure_ascii=False, indent=4)
    
    return birds_data

# Función para obtener datos detallados de cada ave
def fetch_bird_details(birds_data):
    # Verificar si ya existe el archivo de detalles
    if os.path.exists('birds_details.json'):
        try:
            with open('birds_details.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar el archivo de detalles: {e}")
            # Si hay error al cargar, continuamos con la obtención de datos
    
    birds_with_details = []
    
    for i, bird in enumerate(birds_data):
        # Inicializar campos de detalles con valores predeterminados
        bird['habitat'] = 'No disponible'
        bird['order'] = 'No disponible'
        bird['family'] = 'No disponible'
        bird['size'] = 'No disponible'
        
        try:
            # Verificar que _links y self existan y sean diccionarios
            if '_links' in bird and isinstance(bird['_links'], dict) and 'self' in bird['_links']:
                detail_url = bird['_links']['self']
                
                # Verificar que la URL sea una cadena
                if isinstance(detail_url, str):
                    detail_response = requests.get(detail_url)
                    detail_response.raise_for_status()
                    bird_detail = detail_response.json()
                    
                    # Añadir detalles al objeto del ave con verificación de tipos
                    if isinstance(bird_detail, dict):
                        bird['habitat'] = bird_detail.get('habitat', 'No disponible')
                        
                        # Verificar que order sea un diccionario
                        if isinstance(bird_detail.get('order'), dict):
                            bird['order'] = bird_detail['order'].get('name', 'No disponible')
                        
                        # Verificar que family sea un diccionario
                        if isinstance(bird_detail.get('family'), dict):
                            bird['family'] = bird_detail['family'].get('name', 'No disponible')
                        
                        bird['size'] = bird_detail.get('size', 'No disponible')
        except Exception as e:
            print(f"Error al obtener detalles para {bird['name']['spanish']}: {e}")
            # Los valores predeterminados ya están establecidos
        
        birds_with_details.append(bird)
        
        # Esperar un poco entre solicitudes para no sobrecargar la API
        if i < len(birds_data) - 1:
            time.sleep(0.2)
    
    # Guardar los detalles en un archivo JSON para uso futuro
    try:
        with open('birds_details.json', 'w', encoding='utf-8') as f:
            json.dump(birds_with_details, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar el archivo de detalles: {e}")
    
    return birds_with_details

# Función para renderizar el template
def render_html(birds):
    env = Environment(loader=FileSystemLoader('.'))
    # Añadir filtro para formatear texto
    env.filters['lower'] = lambda x: x.lower() if x else ''
    template = env.get_template('template.html')
    html_content = template.render(birds=birds)
    with open('aves_de_chile.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

# Función principal
def main():
    print("Obteniendo datos de aves de Chile...")
    birds_data = fetch_birds_data()
    
    print("Obteniendo detalles adicionales de cada ave...")
    birds_with_details = fetch_bird_details(birds_data)
    
    print("Generando página HTML...")
    render_html(birds_with_details)
    
    print("¡Proceso completado! Se ha generado el archivo 'aves_de_chile.html'")
    print("Puedes abrirlo en tu navegador para ver el resultado.")

if __name__ == '__main__':
    main()