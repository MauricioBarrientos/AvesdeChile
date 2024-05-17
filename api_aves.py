import requests
from jinja2 import Environment, FileSystemLoader

# Función para obtener datos de la API
def fetch_birds_data():
    url = 'https://aves.ninjas.cl/api/birds'
    response = requests.get(url)
    response.raise_for_status()  # Levantar una excepción si la respuesta contiene un error
    return response.json()

# Función para renderizar el template
def render_html(birds):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_content = template.render(birds=birds)
    with open('aves_de_chile.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

# Función principal
def main():
    birds_data = fetch_birds_data()
    render_html(birds_data)

if __name__ == '__main__':
    main()