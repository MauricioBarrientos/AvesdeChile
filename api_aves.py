import requests
from jinja2 import Environment, FileSystemLoader
import random
import time
import json
import os
import shutil
from urllib.parse import urlparse

# Función para descargar una imagen y guardarla localmente
def download_image(image_url, save_path):
    try:
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Verificar si la imagen ya existe
        if os.path.exists(save_path):
            print(f"Imagen ya existe: {save_path}")
            return save_path
        
        # Descargar la imagen
        print(f"Descargando imagen: {image_url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Guardar la imagen
        with open(save_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)
        
        print(f"Imagen descargada: {save_path}")
        return save_path
    except Exception as e:
        print(f"Error al descargar la imagen {image_url}: {e}")
        return None

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

# Función para extraer regiones de Chile del texto de hábitat
def extract_regions(habitat_text):
    regions = [
        "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama", "Coquimbo", 
        "Valparaíso", "Metropolitana", "O'Higgins", "Maule", "Ñuble", "Biobío", 
        "Araucanía", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"
    ]
    
    found_regions = []
    if habitat_text and isinstance(habitat_text, str):
        for region in regions:
            if region.lower() in habitat_text.lower():
                found_regions.append(region)
        
        # Casos especiales
        if "cabo de hornos" in habitat_text.lower():
            if "Magallanes" not in found_regions:
                found_regions.append("Magallanes")
        if "santiago" in habitat_text.lower() and "Metropolitana" not in found_regions:
            found_regions.append("Metropolitana")
    
    return found_regions if found_regions else ["No especificada"]

# Función para obtener datos detallados de cada ave y descargar imágenes
def fetch_bird_details(birds_data):
    # Crear directorio para imágenes si no existe
    images_dir = os.path.join(os.getcwd(), 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Directorio de imágenes creado: {images_dir}")
    
    # Verificar si ya existe el archivo de detalles
    if os.path.exists('birds_details.json'):
        try:
            with open('birds_details.json', 'r', encoding='utf-8') as f:
                birds_with_details = json.load(f)
                
                # Verificar si necesitamos descargar imágenes para datos existentes
                for bird in birds_with_details:
                    if 'image_url' in bird and bird['image_url'].startswith('http'):
                        # Extraer el nombre del archivo de la URL
                        parsed_url = urlparse(bird['image_url'])
                        filename = os.path.basename(parsed_url.path)
                        local_path = os.path.join('images', filename)
                        
                        # Descargar la imagen si no existe localmente
                        downloaded_path = download_image(bird['image_url'], local_path)
                        if downloaded_path:
                            # Actualizar la URL de la imagen a la ruta local
                            bird['image_url'] = downloaded_path
                
                # Guardar los datos actualizados
                with open('birds_details.json', 'w', encoding='utf-8') as f:
                    json.dump(birds_with_details, f, ensure_ascii=False, indent=4)
                
                return birds_with_details
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
        
        # Descargar la imagen del ave
        if 'images' in bird and 'main' in bird['images']:
            image_url = bird['images']['main']
            # Extraer el nombre del archivo de la URL
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            # Asegurar que el nombre del archivo sea único
            safe_filename = f"{i}_{filename}"
            local_path = os.path.join('images', safe_filename)
            
            # Descargar la imagen
            downloaded_path = download_image(image_url, local_path)
            if downloaded_path:
                # Actualizar la URL de la imagen a la ruta local
                bird['image_url'] = downloaded_path
            else:
                # Mantener la URL original si la descarga falla
                bird['image_url'] = image_url
        
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
                        
                        # Extraer regiones del hábitat
                        bird['regions'] = extract_regions(bird['habitat'])
                        
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
    
    random.shuffle(birds_with_details)
    
    print("Generando página HTML...")
    render_html(birds_with_details)
    
    print("¡Proceso completado! Se ha generado el archivo 'aves_de_chile.html'")
    print("Puedes abrirlo en tu navegador para ver el resultado.")

if __name__ == '__main__':
    main()