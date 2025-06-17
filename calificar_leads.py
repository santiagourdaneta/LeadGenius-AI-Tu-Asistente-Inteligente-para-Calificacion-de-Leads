import pandas as pd
import sqlite3
import joblib
import datetime
import numpy as np # Para manejar NaNs

def cargar_modelo(path='cerebro_adivinador.pkl'):
    """Carga el modelo entrenado."""
    try:
        modelo = joblib.load(path)
        print("Cerebro Adivinador cargado.")
        return modelo
    except FileNotFoundError:
        print(f"Error: Modelo no encontrado en {path}. Asegúrate de haber ejecutado 'modelo_calificacion.py' primero.")
        return None

def calificar_nuevos_leads():
    """
    Carga menciones no calificadas, aplica el modelo y guarda los resultados.
    """
    conn = sqlite3.connect('diario_leads.db')
    
    try:
       # Obtener los leads de 'menciones_nuevas' que AÚN NO están en 'leads_calificados'
        # Esto asume que tienes un identificador único para cada lead, como 'nombre' y 'email'.
        # En un sistema real, idealmente cada fila tendría un ID único.
        
        # Primero, cargamos todos los leads de 'menciones_nuevas'
        df_todas_menciones = pd.read_sql_query("SELECT * FROM menciones_nuevas", conn)

        # Luego, cargamos los leads que ya han sido calificados
        # Manejamos el caso si la tabla leads_calificados aún no existe
        try:
            df_calificados_existentes = pd.read_sql_query("SELECT nombre, email FROM leads_calificados", conn)
        except pd.io.sql.DatabaseError:
            df_calificados_existentes = pd.DataFrame(columns=['nombre', 'email']) # Si la tabla no existe, dataframe vacío

        # Identificamos los leads que ya están calificados usando 'nombre' y 'email' como identificadores
        # Esto puede no ser 100% robusto si hay nombres/emails duplicados pero es un buen inicio.
        # Si tuvieras un 'lead_id' en menciones_nuevas, sería mejor usarlo.
        merged_df = pd.merge(df_todas_menciones, df_calificados_existentes, on=['nombre', 'email'], how='left', indicator=True)
        df_nuevos_leads = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])

        if df_nuevos_leads.empty:
            print("No hay nuevos leads para calificar.")
            return

        modelo = cargar_modelo()
        if modelo is None:
            return

        # Preparar las características para la predicción, igual que en el entrenamiento
        # Asegurarse de que todas las columnas necesarias existan y estén en el formato correcto
        df_nuevos_leads['mensaje_longitud'] = df_nuevos_leads['mensaje'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
        df_nuevos_leads['mensaje_contiene_precios'] = df_nuevos_leads['mensaje'].str.contains('precios|cotizacion', case=False, na=False).astype(int)
        df_nuevos_leads['mensaje_contiene_demo'] = df_nuevos_leads['mensaje'].str.contains('demo', case=False, na=False).astype(int)

        # Manejar posibles valores nulos en las columnas que usamos para predecir
        # Puedes decidir si rellenar con 0, la media, o eliminar la fila.
        # Aquí rellenamos con 0 para este ejemplo.
        df_nuevos_leads['comportamiento'] = df_nuevos_leads['comportamiento'].fillna(0).astype(int)
        df_nuevos_leads['interaccion_email'] = df_nuevos_leads['interaccion_email'].fillna(0).astype(int)
        
        # Las características deben ser las mismas que se usaron para entrenar el modelo
        features = ['comportamiento', 'interaccion_email', 'mensaje_longitud', 'mensaje_contiene_precios', 'mensaje_contiene_demo']
        
        X_predict = df_nuevos_leads[features]
        
        # Predecir la probabilidad de que sea un "buen lead" (puntuacion_intencion)
        # predict_proba devuelve las probabilidades para cada clase (0 y 1).
        # Queremos la probabilidad de la clase 1 (es_buen_lead=1).
        df_nuevos_leads['puntuacion_intencion'] = modelo.predict_proba(X_predict)[:, 1] * 100 # Multiplicar por 100 para porcentaje

        # --- Simulación de 'necesidad_diagnosticada' ---
        # Esto en la realidad sería otro modelo (NLP) o reglas de negocio
        df_nuevos_leads['necesidad_diagnosticada'] = np.where(
            df_nuevos_leads['mensaje_contiene_precios'] == 1, 
            'Necesidad de Precios/Cotización',
            np.where(df_nuevos_leads['mensaje_contiene_demo'] == 1, 
                     'Interés en Demostración', 
                     'Interés General')
        )
        
        # Actualizar la base de datos con los resultados
        # Utilizaremos la columna 'id' para actualizar los registros existentes
        # Asegúrate de que tu tabla 'menciones_nuevas' tenga una columna 'id' AUTOINCREMENT
        
        # Crea una nueva tabla para leads calificados o actualiza la existente si tiene IDs.
        # Para este ejemplo, crearemos una nueva tabla 'leads_calificados'
        
        # --- ¡NUEVA LÍNEA CLAVE AQUÍ! ---
        # Aseguramos que la columna 'fecha_alerta' exista con valores nulos (NULL)
        df_nuevos_leads['fecha_alerta'] = None 
        # --- FIN NUEVA LÍNEA ---

        df_nuevos_leads.to_sql('leads_calificados', conn, if_exists='append', index=False)
        print(f"Se calificaron {len(df_nuevos_leads)} nuevos leads y se guardaron en 'leads_calificados'.")

        # Opcional: Marcar los leads como calificados en la tabla original 'menciones_nuevas'
        # Puedes hacerlo si 'menciones_nuevas' tiene un 'id' para cada fila
        # update_query = """
        # UPDATE menciones_nuevas
        # SET puntuacion_intencion = ?, necesidad_diagnosticada = ?
        # WHERE id = ?
        # """
        # for index, row in df_nuevos_leads.iterrows():
        #     conn.execute(update_query, (row['puntuacion_intencion'], row['necesidad_diagnosticada'], row['id']))
        # conn.commit()
        
    except Exception as e:
        print(f"Error durante la calificación de leads: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando proceso de calificación de leads...")
    calificar_nuevos_leads()