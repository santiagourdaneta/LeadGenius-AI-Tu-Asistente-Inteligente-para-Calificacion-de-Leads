# ai_brain.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import nltk # Para procesar texto
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import re # Para limpiar texto

# Necesitamos estas funciones de db_manager para hablar con el diario
from db_manager import get_all_menciones, add_calified_lead, get_all_leads_calificados, get_all_empresas, DB_NAME
import sqlite3

# --- Descarga de recursos de NLTK (ajustado para capturar LookupError) ---
# Hemos intentado descargar antes, pero este bloque es para asegurar que si faltan, se pida.
# Sin embargo, como ya los descargamos manualmente, esta sección es más por robustez.
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError: # <--- ¡CAMBIO AQUÍ! Capturamos LookupError directamente
    print("Descargando recursos de NLTK (stopwords, punkt)... esto solo se hace una vez.")
    nltk.download('stopwords')
    nltk.download('punkt')
    print("Recursos de NLTK descargados.")


# --- Preparar los "Libros de Entrenamiento" del Cerebro ---
def prepare_training_data():
    """
    Crea datos de entrenamiento simulados. En un proyecto real,
    estos serían datos de clientes pasados (ej. de tu CRM).
    """
    data = {
        'texto_mencion': [
            "Nuestra empresa busca soluciones de automatización para optimizar procesos.",
            "Estamos expandiendo operaciones y necesitamos un nuevo CRM.",
            "Publicaron resultados financieros muy positivos, gran crecimiento.",
            "Anunciaron un despido masivo, están en reestructuración.",
            "Buscan consultores para eficiencia energética.",
            "Nuevo CEO con visión de digitalización avanzada.",
            "Quejas de clientes en redes sociales por mal servicio al cliente.",
            "Necesitan mejorar su infraestructura de la nube urgentemente.",
            "Acaban de lanzar un producto innovador en el mercado de IA.",
            "Reportan pérdidas por problemas en la cadena de suministro.",
            "Preocupados por la seguridad de sus datos y ataques cibernéticos.",
            "Implementarán nuevo software de gestión de proyectos para mejorar la colaboración."
        ],
        'es_lead_calificado': [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1], # 1: Buen lead, 0: Mal lead
        'necesidad_real': [
            "Automatización de procesos",
            "Gestión de relaciones con clientes (CRM)",
            "Ninguna (enfoque financiero)",
            "Ninguna (problemas internos)",
            "Eficiencia energética",
            "Digitalización / Innovación",
            "Mejora de servicio al cliente",
            "Infraestructura Cloud / DevOps",
            "Ninguna (enfoque en producto existente)",
            "Ninguna (problemas operativos)",
            "Ciberseguridad",
            "Gestión de proyectos"
        ]
    }
    return pd.DataFrame(data)

# --- Limpieza de Texto (para que el Cerebro entienda mejor) ---
stemmer = SnowballStemmer('spanish')
stopwords_es = set(stopwords.words('spanish'))

def clean_text(text):
    text = text.lower() # Todo a minúsculas
    text = re.sub(r'\d+', '', text) # Quitar números
    text = re.sub(r'[^\w\s]', '', text) # Quitar puntuación
    tokens = nltk.word_tokenize(text) # Dividir en palabras
    tokens = [word for word in tokens if word not in stopwords_es] # Quitar palabras comunes
    tokens = [stemmer.stem(word) for word in tokens] # Reducir palabras a su raíz (ej. "corriendo" -> "corr")
    return " ".join(tokens)

# --- Entrenar al Cerebro Adivinador ---
def train_ai_brain():
    """
    Entrena el modelo de IA para clasificar leads y diagnosticar necesidades.
    """
    df_train = prepare_training_data()
    df_train['texto_limpio'] = df_train['texto_mencion'].apply(clean_text)

    # Vectorizador para convertir texto en números que la IA entienda
    vectorizer = TfidfVectorizer(max_features=1000) # Solo las 1000 palabras más importantes
    X_text = vectorizer.fit_transform(df_train['texto_limpio'])

    # Entrenar modelo para PREDECIR si es un buen lead
    model_calificacion = LogisticRegression(random_state=42, solver='liblinear')
    model_calificacion.fit(X_text, df_train['es_lead_calificado'])

    # Entrenar modelo para DIAGNOSTICAR la necesidad
    encoder_necesidad = LabelEncoder()
    df_train['necesidad_encoded'] = encoder_necesidad.fit_transform(df_train['necesidad_real'])
    model_necesidad = LogisticRegression(random_state=42, solver='liblinear')
    model_necesidad.fit(X_text, df_train['necesidad_encoded'])

    return model_calificacion, model_necesidad, vectorizer, encoder_necesidad

# --- Calificar Nuevos Leads ---
def qualify_new_leads():
    """
    Lee nuevas menciones del diario, las califica con la IA y guarda los resultados.
    """
    model_calificacion, model_necesidad, vectorizer, encoder_necesidad = train_ai_brain()
    
    # Obtener todas las menciones (asumimos que todas podrían necesitar recalificación)
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT m.id AS mencion_id, m.empresa_id, m.texto_mencion, m.fecha_mencion, e.nombre AS nombre_empresa
        FROM menciones m
        JOIN empresas e ON m.empresa_id = e.id
    """
    df_menciones = pd.read_sql_query(query, conn)
    conn.close()

    if df_menciones.empty:
        return "No hay nuevas menciones en el diario para calificar."

    # Limpiar y transformar el texto de las nuevas menciones
    df_menciones['texto_limpio'] = df_menciones['texto_mencion'].apply(clean_text)
    X_new_text = vectorizer.transform(df_menciones['texto_limpio'])

    # Predicción de calificación (0 o 1) y probabilidad (0 a 1)
    pred_calificacion = model_calificacion.predict(X_new_text)
    pred_proba = model_calificacion.predict_proba(X_new_text)[:, 1] # Probabilidad de ser clase 1 (buen lead)

    # Predicción de necesidad
    pred_necesidad_encoded = model_necesidad.predict(X_new_text)
    pred_necesidad = encoder_necesidad.inverse_transform(pred_necesidad_encoded)

    calificados_count = 0
    for i, row in df_menciones.iterrows():
        if pred_calificacion[i] == 1: # Si la IA dice que es un buen lead
            puntuacion = int(pred_proba[i] * 100) # Convertir a escala de 0 a 100
            necesidad = pred_necesidad[i]
            
            success, msg = add_calified_lead(row['empresa_id'], puntuacion, necesidad)
            if success:
                calificados_count += 1
            else:
                print(f"Error al guardar lead calificado para {row['nombre_empresa']}: {msg}")

    return f"¡Cerebro Adivinador: {calificados_count} leads calificados y actualizados en el diario!"

if __name__ == '__main__':
    # Asegúrate de que db_manager.py ya creó el leads.db y tienes algunas menciones
    # Puedes ejecutar db_manager.py primero con los ejemplos de add_empresa y add_mencion
    # Luego, ejecuta este archivo: python ai_brain.py

    print("Iniciando calificación de leads con el Cerebro Adivinador...")
    status = qualify_new_leads()
    print(status)

    print("\nLeads calificados en el diario:")
    print(get_all_leads_calificados())