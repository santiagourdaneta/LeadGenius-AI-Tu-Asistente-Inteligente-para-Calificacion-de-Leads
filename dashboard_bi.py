import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generar_reporte_leads():
    """Genera un resumen y visualizaciones de los leads calificados."""
    conn = sqlite3.connect('diario_leads.db')
    try:
        df_calificados = pd.read_sql_query("SELECT * FROM leads_calificados", conn)
        
        if df_calificados.empty:
            print("No hay leads calificados para generar el reporte.")
            return

        print("\n--- Resumen de Leads Calificados ---")
        print(f"Total de leads calificados: {len(df_calificados)}")
        print("\nDistribución de Puntuación de Intención:")
        print(df_calificados['puntuacion_intencion'].describe())

        print("\nNecesidades Diagnosticadas Más Comunes:")
        print(df_calificados['necesidad_diagnosticada'].value_counts())

        print("\nFuentes de Leads Calificados:")
        print(df_calificados['fuente'].value_counts())

        # --- Visualizaciones ---
        plt.figure(figsize=(15, 6))

        # Histograma de puntuación de intención
        plt.subplot(1, 2, 1) # 1 fila, 2 columnas, 1ra posición
        sns.histplot(df_calificados['puntuacion_intencion'], bins=10, kde=True)
        plt.title('Distribución de Puntuación de Intención')
        plt.xlabel('Puntuación de Intención (%)')
        plt.ylabel('Cantidad de Leads')

        # Gráfico de barras de necesidades diagnosticadas
        plt.subplot(1, 2, 2) # 1 fila, 2 columnas, 2da posición
        sns.countplot(y='necesidad_diagnosticada', data=df_calificados, order=df_calificados['necesidad_diagnosticada'].value_counts().index)
        plt.title('Necesidades Diagnosticadas')
        plt.xlabel('Cantidad de Leads')
        plt.ylabel('Necesidad')
        plt.tight_layout()
        plt.show()

        # Gráfico de barras de fuentes de leads
        plt.figure(figsize=(8, 5))
        sns.countplot(y='fuente', data=df_calificados, order=df_calificados['fuente'].value_counts().index)
        plt.title('Fuentes de Leads Calificados')
        plt.xlabel('Cantidad de Leads')
        plt.ylabel('Fuente')
        plt.show()

    except pd.io.sql.DatabaseError as e:
        print(f"Error al cargar datos de la base de datos: {e}. Asegúrate de que 'diario_leads.db' y 'leads_calificados' existen.")
    finally:
        conn.close()

def enviar_alerta_leads_altos(umbral=80):
    """
    Envía un email de alerta si hay leads con alta puntuación de intención.
    """
    conn = sqlite3.connect('diario_leads.db')
    try:
        df_calificados = pd.read_sql_query(f"SELECT * FROM leads_calificados WHERE puntuacion_intencion >= {umbral} AND fecha_alerta IS NULL", conn)
        
        if df_calificados.empty:
            print(f"No hay nuevos leads con puntuación >= {umbral} para alertar.")
            return

        print(f"\n--- Alerta: ¡Se encontraron {len(df_calificados)} leads de alta intención! ---")
        print(df_calificados[['nombre', 'email', 'puntuacion_intencion', 'necesidad_diagnosticada', 'fuente']])

        # --- Configuración para enviar el email (ADAPTA ESTO CON TUS DATOS REALES) ---
        sender_email = "tu_email@gmail.com" # Tu email
        sender_password = "tu_contraseña_de_aplicacion" # Contraseña de aplicación si usas Gmail
        receiver_email = "equipo_ventas@tuempresa.com" # Email del equipo de ventas
        subject = f"¡NUEVOS LEADS DE ALTA INTENCIÓN ({len(df_calificados)})!"

        body = "Hola equipo,\n\nSe han identificado los siguientes leads de alta intención:\n\n"
        for index, row in df_calificados.iterrows():
            body += f"- Nombre: {row['nombre']}, Email: {row['email']}\n"
            body += f"  Intención: {row['puntuacion_intencion']:.2f}%, Necesidad: {row['necesidad_diagnosticada']}\n"
            body += f"  Fuente: {row['fuente']}\n\n"
        body += "Por favor, revisen y contacten a la brevedad.\n\nSaludos,\nTu Robot Calificador"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Para Gmail, usar 'smtp.gmail.com' y puerto 587
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls() # Habilitar seguridad
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print(f"¡Alerta de leads enviada a {receiver_email}!")
            
            # Marcar los leads como alertados para no enviarles otra vez la misma alerta
            # Tendrías que añadir una columna 'fecha_alerta' en tu tabla 'leads_calificados'
            conn.execute(f"UPDATE leads_calificados SET fecha_alerta = ? WHERE puntuacion_intencion >= {umbral} AND fecha_alerta IS NULL", (datetime.datetime.now().isoformat(),))
            conn.commit()

        except Exception as e:
            print(f"Error al enviar email de alerta: {e}")
            print("Asegúrate de que tu email y contraseña de aplicación son correctos.")
            print("Si usas Gmail, podrías necesitar generar una 'contraseña de aplicación' en la configuración de seguridad de Google.")
            print("Busca 'Contraseñas de aplicación Google' para más información.")
        finally:
            server.quit()

    except pd.io.sql.DatabaseError as e:
        print(f"Error al cargar datos de la base de datos para la alerta: {e}.")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Generando reporte de Inteligencia de Negocios...")
    generar_reporte_leads()
    
    print("\nVerificando leads de alta intención para enviar alertas...")
    enviar_alerta_leads_altos(umbral=80) # Puedes ajustar el umbral de alerta (ej. 80%)