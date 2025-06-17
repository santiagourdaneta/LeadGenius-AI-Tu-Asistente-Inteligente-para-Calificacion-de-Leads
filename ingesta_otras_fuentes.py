import pandas as pd
import sqlite3
import datetime

def ingestar_formulario_contacto(nombre, email, mensaje):
    """Simula la recepción de un formulario de contacto."""
    data = [{
        'nombre': nombre,
        'email': email,
        'mensaje': mensaje,
        'fuente': 'formulario_web',
        'fecha_mencion': datetime.datetime.now().isoformat(),
        'comportamiento': 1, # Indicador de que llenó un formulario
        'interaccion_email': 0 # Puede actualizarse si luego interactúa con emails
    }]
    df = pd.DataFrame(data)
    guardar_en_bd(df)

def ingestar_csv_evento(ruta_archivo_csv):
    """Ingesta datos de un archivo CSV de un evento/feria."""
    try:
        df = pd.read_csv(ruta_archivo_csv)
        # Asegurarse de que las columnas coincidan o mapearlas
        df['fuente'] = 'evento_csv'
        df['fecha_mencion'] = datetime.datetime.now().isoformat()
        df['comportamiento'] = 0 # Valor por defecto
        df['interaccion_email'] = 0 # Valor por defecto
        
        # Renombrar columnas si es necesario para que coincidan con el esquema de la BD
        df = df.rename(columns={'NombreEmpresa': 'nombre', 'ContactoEmail': 'email', 'Detalles': 'mensaje'})
        # Asegúrate de que las columnas esperadas existan antes de guardar
        columnas_esperadas = ['nombre', 'email', 'mensaje', 'fuente', 'fecha_mencion', 'comportamiento', 'interaccion_email']
        df_final = df[columnas_esperadas] if all(col in df.columns for col in columnas_esperadas) else pd.DataFrame(columns=columnas_esperadas)
        
        guardar_en_bd(df_final)
    except FileNotFoundError:
        print(f"Error: El archivo CSV '{ruta_archivo_csv}' no se encontró.")
    except Exception as e:
        print(f"Error al leer o procesar el CSV: {e}")

def guardar_en_bd(dataframe, nombre_tabla='menciones_nuevas'):
    """
    Función auxiliar para guardar el DataFrame en la base de datos SQLite.
    """
    conn = sqlite3.connect('diario_leads.db')
    try:
        dataframe.to_sql(nombre_tabla, conn, if_exists='append', index=False)
        print(f"Datos de '{dataframe['fuente'].iloc[0]}' guardados en la tabla '{nombre_tabla}'.")
    except Exception as e:
        print(f"Error al guardar datos en SQLite: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Simulando ingesta de otras fuentes...")

    # Ejemplo de un lead de formulario de contacto
    ingestar_formulario_contacto("Juan Perez", "juan.perez@ejemplo.com", "Quiero saber mas de sus productos.")

    # Ejemplo de un lead de un archivo CSV (crea un archivo 'leads_evento.csv' con datos de ejemplo)
    # Crea un archivo 'leads_evento.csv' con este contenido:
    # NombreEmpresa,ContactoEmail,Detalles
    # Tech Solutions,info@tech.com,Interesados en software
    # Global Innovations,sales@global.com,Necesitan consultoria
    ingestar_csv_evento('leads_evento.csv')