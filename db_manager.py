# db_manager.py

import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = 'leads.db' # Este será nuestro archivo de diario secreto

def init_db():
    """
    Inicializa la base de datos SQLite y crea las tablas si no existen.
    Esto asegura que tenemos un lugar donde guardar todas nuestras pistas.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Página para guardar la información de las empresas (los "niños")
    c.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE, -- El nombre debe ser único, como el nombre de un niño
            url TEXT,
            industria TEXT,
            localidad TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Página para guardar las menciones o pistas que encuentran los "Rastreadores Relámpago"
    c.execute('''
        CREATE TABLE IF NOT EXISTS menciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL, -- A qué empresa pertenece esta pista
            texto_mencion TEXT NOT NULL, -- Lo que se dijo de la empresa
            fuente TEXT,                 -- De dónde viene la pista (ej. 'Twitter', 'Noticia')
            fecha_mencion TEXT NOT NULL, -- Cuándo se encontró la pista
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )
    ''')

    # Página para guardar las empresas que el "Gran Cerebro Adivinador" ha calificado como buenos leads
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads_calificados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL UNIQUE, -- Cada empresa calificada solo una vez
            puntuacion_intencion INTEGER NOT NULL, -- Qué tan interesado parece (ej. del 0 al 100)
            necesidad_diagnosticada TEXT,        -- Qué juguete podría necesitar
            fecha_calificacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Base de datos '{DB_NAME}' y tablas inicializadas. ¡Diario listo!")

def add_empresa(nombre, url='', industria='', localidad=''):
    """Añade una nueva empresa al diario si no existe, o devuelve su ID si ya existe."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO empresas (nombre, url, industria, localidad) VALUES (?, ?, ?, ?)",
                  (nombre, url, industria, localidad))
        conn.commit()
        return c.lastrowid, "Empresa añadida."
    except sqlite3.IntegrityError:
        # Si ya existe, obtenemos su ID
        c.execute("SELECT id FROM empresas WHERE nombre = ?", (nombre,))
        empresa_id = c.fetchone()[0]
        return empresa_id, "Empresa ya existe."
    finally:
        conn.close()

def add_mencion(empresa_id, texto_mencion, fuente, fecha_mencion):
    """Añade una pista (mención) para una empresa al diario."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO menciones (empresa_id, texto_mencion, fuente, fecha_mencion) VALUES (?, ?, ?, ?)",
                  (empresa_id, texto_mencion, fuente, fecha_mencion))
        conn.commit()
        return True, "Mención añadida."
    except Exception as e:
        return False, f"Error al añadir mención: {e}"
    finally:
        conn.close()

def add_calified_lead(empresa_id, puntuacion_intencion, necesidad_diagnosticada):
    """Añade o actualiza un lead calificado por el Cerebro Adivinador."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO leads_calificados (empresa_id, puntuacion_intencion, necesidad_diagnosticada)
            VALUES (?, ?, ?)
        ''', (empresa_id, puntuacion_intencion, necesidad_diagnosticada))
        conn.commit()
        return True, "Lead calificado añadido."
    except sqlite3.IntegrityError:
        # Si ya existe, actualizamos la calificación
        c.execute('''
            UPDATE leads_calificados
            SET puntuacion_intencion = ?, necesidad_diagnosticada = ?, fecha_calificacion = CURRENT_TIMESTAMP
            WHERE empresa_id = ?
        ''', (puntuacion_intencion, necesidad_diagnosticada, empresa_id))
        conn.commit()
        return True, "Lead calificado actualizado."
    except Exception as e:
        return False, f"Error al calificar lead: {e}"
    finally:
        conn.close()

def get_all_empresas():
    """Obtiene todas las empresas como DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM empresas", conn)
    conn.close()
    return df

def get_all_menciones():
    """Obtiene todas las menciones como DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM menciones", conn)
    conn.close()
    return df

def get_all_leads_calificados():
    """Obtiene todos los leads calificados (con datos de empresa) como DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query('''
        SELECT 
            lc.id AS lead_id,
            e.nombre AS nombre_empresa, 
            e.industria, 
            e.localidad, 
            e.url,
            lc.puntuacion_intencion, 
            lc.necesidad_diagnosticada, 
            lc.fecha_calificacion
        FROM leads_calificados lc
        JOIN empresas e ON lc.empresa_id = e.id
        ORDER BY lc.fecha_calificacion DESC
    ''', conn)
    conn.close()
    return df

def get_menciones_by_empresa(empresa_id):
    """Obtiene menciones para una empresa específica."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM menciones WHERE empresa_id = ?", conn, params=(empresa_id,))
    conn.close()
    return df

if __name__ == '__main__':
    init_db()
    # Ejemplos de uso para probar el diario (puedes borrarlos después)
    # id1, msg1 = add_empresa("TechInnovators", "https://techinnovators.com", "Tecnología", "Ciudad Futura")
    # id2, msg2 = add_empresa("EcoSolutions", "https://ecosolutions.net", "Medio Ambiente", "Pueblo Verde")
    # print(msg1, id1)
    # print(msg2, id2)

    # success, msg = add_mencion(id1, "Buscan automatizar sus procesos.", "Noticia Local", "2024-06-01")
    # print(msg)
    # success, msg = add_mencion(id1, "Contrataron nuevo CTO para digitalización.", "LinkedIn", "2024-06-05")
    # print(msg)
    # success, msg = add_mencion(id2, "Preocupados por eficiencia energética.", "Foro Industrial", "2024-05-20")
    # print(msg)

    # success, msg = add_calified_lead(id1, 85, "Necesidad de automatización de software.")
    # print(msg)
    # success, msg = add_calified_lead(id2, 70, "Búsqueda de soluciones energéticas renovables.")
    # print(msg)

    # print("\nTodas las empresas:")
    # print(get_all_empresas())
    # print("\nTodas las menciones:")
    # print(get_all_menciones())
    # print("\nTodos los leads calificados:")
    # print(get_all_leads_calificados())