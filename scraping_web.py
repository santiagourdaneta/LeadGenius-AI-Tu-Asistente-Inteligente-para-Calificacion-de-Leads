import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import datetime

def scrape_data(url):
    """
    Función para raspar datos de una URL específica.
    En un escenario real, adaptarías esto para cada sitio web.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza un error para códigos de estado HTTP incorrectos
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la URL {url}: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # --- EJEMPLO SIMPLIFICADO: ADAPTA ESTO A LA ESTRUCTURA DE LA WEB QUE QUIERAS RASPAR ---
    # Esto es solo un ejemplo. Necesitas inspeccionar el HTML de la página real
    # para saber qué etiquetas y clases buscar.
    
    leads_encontrados = []
    # Suponemos que cada "lead" está dentro de un div con la clase 'lead-item'
    # y dentro tiene un h2 con el nombre y un p con la descripción
    for item in soup.find_all('div', class_='lead-item'):
        nombre = item.find('h2', class_='lead-name').text.strip() if item.find('h2', class_='lead-name') else 'N/A'
        descripcion = item.find('p', class_='lead-description').text.strip() if item.find('p', class_='lead-description') else 'N/A'
        leads_encontrados.append({'nombre': nombre, 'descripcion': descripcion, 'fuente': 'web_scraping', 'fecha_mencion': datetime.datetime.now().isoformat()})
    # --- FIN DEL EJEMPLO SIMPLIFICADO ---

    return pd.DataFrame(leads_encontrados)

def guardar_en_bd(dataframe, nombre_tabla='menciones_nuevas'):
    """
    Guarda el DataFrame en la base de datos SQLite.
    """
    conn = sqlite3.connect('diario_leads.db')
    try:
        dataframe.to_sql(nombre_tabla, conn, if_exists='append', index=False)
        print(f"Datos de web scraping guardados en la tabla '{nombre_tabla}'.")
    except Exception as e:
        print(f"Error al guardar datos en SQLite: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando web scraping...")
    
    # URL de ejemplo. ¡CAMBIA ESTO por la URL real que quieres raspar!
    url_a_raspar = "http://ejemplo.com/directorio-empresas" # Reemplaza con una URL real
    
    nuevos_leads_web = scrape_data(url_a_raspar)
    
    if not nuevos_leads_web.empty:
        # Añadir columnas que puedan ser útiles para el modelo
        nuevos_leads_web['comportamiento'] = 0 # Valor por defecto, se puede actualizar
        nuevos_leads_web['interaccion_email'] = 0 # Valor por defecto
        # Otras columnas como 'industria', 'tamano_empresa', si puedes extraerlas o inferirlas.

        guardar_en_bd(nuevos_leads_web)
    else:
        print("No se encontraron nuevos leads mediante web scraping o hubo un error.")