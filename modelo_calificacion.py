import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib # Para guardar y cargar el modelo

# --- Paso 1: Preparar los datos para el entrenamiento ---
def cargar_datos_entrenamiento():
    """Carga los datos de menciones y simula una etiqueta de 'intención'."""
    conn = sqlite3.connect('diario_leads.db')
    try:
        # Cargamos todas las menciones
        df = pd.read_sql_query("SELECT * FROM menciones_nuevas", conn)
        
        # --- MUY IMPORTANTE: SIMULACIÓN DE LA ETIQUETA 'es_buen_lead' ---
        # En la vida real, necesitarías una columna que indique si el lead SÍ compró
        # o fue de alto valor. Aquí la simulamos para el ejemplo.
        # Por ejemplo, leads de formulario de contacto tienen más probabilidad de ser buenos,
        # o si el mensaje contiene ciertas palabras clave, o si el comportamiento es alto.
        df['es_buen_lead'] = 0 # Por defecto, no es buen lead
        df.loc[df['fuente'] == 'formulario_web', 'es_buen_lead'] = 1 # Leads de formulario son 1
        df.loc[df['mensaje'].str.contains('precios|demo|cotizacion', case=False, na=False), 'es_buen_lead'] = 1 # Si el mensaje contiene estas palabras, es 1
        df.loc[df['comportamiento'] > 0, 'es_buen_lead'] = 1 # Si el comportamiento es > 0, es 1
        # Asegurarnos de que 'es_buen_lead' sea tipo int
        df['es_buen_lead'] = df['es_buen_lead'].astype(int)

        # Seleccionar las características (columnas) que el modelo usará para aprender
        # Aquí, estamos usando 'comportamiento', 'interaccion_email' y características del mensaje
        # Necesitamos convertir texto a números para el modelo. Esto es simplificado.
        # Para NLP real, usarías TfidfVectorizer o similar.
        df['mensaje_longitud'] = df['mensaje'].apply(lambda x: len(str(x)))
        df['mensaje_contiene_precios'] = df['mensaje'].str.contains('precios|cotizacion', case=False, na=False).astype(int)
        df['mensaje_contiene_demo'] = df['mensaje'].str.contains('demo', case=False, na=False).astype(int)

        features = ['comportamiento', 'interaccion_email', 'mensaje_longitud', 'mensaje_contiene_precios', 'mensaje_contiene_demo']
        
        # Filtramos solo las columnas que vamos a usar como características y la etiqueta
        df_entrenamiento = df.dropna(subset=features + ['es_buen_lead'])

        X = df_entrenamiento[features]
        y = df_entrenamiento['es_buen_lead']
        
        return X, y, features
    except pd.io.sql.DatabaseError as e:
        print(f"Error al cargar datos de la base de datos: {e}. Asegúrate de que 'diario_leads.db' y la tabla 'menciones_nuevas' existen.")
        return pd.DataFrame(), pd.Series(), []
    finally:
        conn.close()

# --- Paso 2: Entrenar el modelo ---
def entrenar_modelo(X, y):
    """Entrena el modelo de clasificación y lo guarda."""
    if X.empty or y.empty:
        print("No hay suficientes datos para entrenar el modelo.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Creamos nuestro "Cerebro Adivinador" (RandomForestClassifier)
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    # Evaluar el modelo (ver qué tan bien adivina)
    y_pred = modelo.predict(X_test)
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, y_pred))
    print(f"Precisión del modelo: {accuracy_score(y_test, y_pred):.2f}")
    
    # Guardar el modelo para usarlo más tarde
    joblib.dump(modelo, 'cerebro_adivinador.pkl')
    print("¡Cerebro Adivinador entrenado y guardado como 'cerebro_adivinador.pkl'!")
    return modelo

# --- Paso 3: Cargar el modelo para predecir ---
def cargar_modelo():
    """Carga un modelo entrenado desde un archivo."""
    try:
        modelo = joblib.load('cerebro_adivinador.pkl')
        print("Cerebro Adivinador cargado con éxito.")
        return modelo
    except FileNotFoundError:
        print("Error: El 'cerebro_adivinador.pkl' no se encontró. Necesitas entrenar el modelo primero.")
        return None

if __name__ == "__main__":
    print("Iniciando entrenamiento del Cerebro Adivinador...")
    X, y, features = cargar_datos_entrenamiento()
    if not X.empty and not y.empty:
        entrenar_modelo(X, y)
        print("Recuerda que para un modelo real, necesitas datos históricos de leads con su resultado final (si compraron o no).")
    else:
        print("No se pudo entrenar el modelo. Asegúrate de tener datos en 'diario_leads.db'.")