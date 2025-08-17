# Aves de Chile

## Descripción del Proyecto

Este proyecto fue desarrollado para la Asociación de Amantes de los Pájaros de Chile, con el objetivo de crear un catálogo digital de aves que pueden ser observadas en Chile. La aplicación muestra imágenes de aves típicas de Chile junto con información relevante como sus nombres en español e inglés, hábitat, orden, familia y tamaño.

La información presentada puede ser utilizada para crear señaléticas bilingües que fomenten el turismo ornitológico en Chile.

## Características

- Visualización de aves de Chile con imágenes de alta calidad
- Información detallada de cada ave (nombre en español e inglés, hábitat, orden, familia, tamaño)
- Búsqueda de aves por nombre en español o inglés
- Interfaz responsiva y moderna
- Almacenamiento local de datos para reducir llamadas a la API

## Tecnologías Utilizadas

- Python 3
- Jinja2 (motor de plantillas)
- HTML5, CSS3 y JavaScript
- API de aves.ninjas.cl

## Cómo Ejecutar el Proyecto

1. Asegúrate de tener Python 3 instalado en tu sistema
2. Instala las dependencias necesarias:
   ```
   pip install requests jinja2
   ```
3. Ejecuta el script principal:
   ```
   python api_aves.py
   ```
4. Abre el archivo `aves_de_chile.html` generado en tu navegador web

Alternativamente, puedes iniciar un servidor web local para visualizar la página:
```
python -m http.server
```
Y luego visitar `http://localhost:8000/aves_de_chile.html` en tu navegador.

## Estructura del Proyecto

- `api_aves.py`: Script principal que obtiene los datos de la API y genera el HTML
- `template.html`: Plantilla Jinja2 para generar la página web
- `aves_de_chile.html`: Página web generada con la información de las aves
- `birds_data.json`: Datos básicos de las aves (generado automáticamente)
- `birds_details.json`: Datos detallados de las aves (generado automáticamente)

## Fuente de Datos

Los datos son obtenidos de la API pública: [https://aves.ninjas.cl/api/birds](https://aves.ninjas.cl/api/birds)
