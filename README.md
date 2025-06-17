
Automatiza la identificación de tus clientes ideales con LeadGenius AI. Este proyecto en Python integra web scraping (BeautifulSoup), bases de datos SQLite y Machine Learning (Scikit-learn) para recolectar, calificar y visualizar leads con alta intención de compra, optimizando tus esfuerzos de ventas.

# LeadGenius AI: Potenciando Tu Estrategia de Leads con Inteligencia Artificial

---

¡Bienvenido a **LeadGenius AI**, la solución inteligente para transformar la gestión de tus **leads**! Este proyecto de código abierto te permite automatizar la **recolección**, **calificación** y **visualización** de potenciales clientes, asegurando que tu equipo de ventas se enfoque en las oportunidades más valiosas.

En el competitivo mundo de los negocios, identificar **leads de alta calidad** es crucial. LeadGenius AI está diseñado para hacer precisamente eso, utilizando el poder de **Python**, **Machine Learning** y **bases de datos eficientes**.

---

## ¿Qué Problema Resuelve LeadGenius AI?

Tradicionalmente, la identificación de **leads** es un proceso manual, lento y propenso a errores. Esto lleva a:
* **Pérdida de tiempo:** Equipos de ventas persiguiendo leads sin intención.
* **Oportunidades perdidas:** No detectar a tiempo clientes muy interesados.
* **Decisiones poco informadas:** Falta de datos claros sobre el comportamiento del lead.

**LeadGenius AI** convierte este desafío en una ventaja, permitiendo un flujo constante de **leads calificados** y listos para la acción.

---

## Características Clave

* **🎣 Recolección de Menciones Nuevas:**
    * **Web Scraping Robusto:** Utiliza **BeautifulSoup** para extraer **leads** de sitios web relevantes (directorios, noticias, blogs).
    * **Integración Flexible:** Soporte para ingesta de datos de **formularios web**, **archivos CSV** (eventos/ferias) y otras fuentes, manteniendo tu "diario" de leads siempre actualizado.
* **🧠 Modelo de Calificación Inteligente (Machine Learning):**
    * Un "Cerebro Adivinador" construido con **Scikit-learn** que predice la **puntuación de intención** de cada lead.
    * Diagnóstico automatizado de las **necesidades del cliente** basado en el contenido de sus interacciones.
    * **Predicción de valor** para priorizar los **leads** con mayor potencial de conversión.
* **📈 Inteligencia de Negocio y Visualización:**
    * **Dashboards Interactivos:** Genera **gráficos y reportes** claros (usando **Matplotlib** y **Seaborn**) para entender la distribución de leads, fuentes efectivas y necesidades comunes.
* **🗄️ Gestión de Datos Confiable:**
    * Almacenamiento eficiente de todas las menciones y leads calificados en una base de datos **SQLite3** local, fácil de gestionar y escalar.
    * Uso de **Pandas** para una manipulación y análisis de datos ágil y potente.

---

## Tecnologías Utilizadas

* **Python 3.x**
* **BeautifulSoup4** (para web scraping)
* **Requests** (para peticiones HTTP)
* **Pandas** (para manipulación y análisis de datos)
* **SQLite3** (como base de datos ligera)
* **Scikit-learn** (para Machine Learning y modelos predictivos)
* **Matplotlib** (para visualización de datos)
* **Seaborn** (para visualización de datos mejorada)
* **joblib** (para serialización de modelos ML)

---

## Instalación y Uso

Sigue estos sencillos pasos para poner en marcha **LeadGenius AI** en tu sistema:

1.  **Clona el Repositorio:**
    ```bash
    git clone https://github.com/santiagourdaneta/LeadGenius-AI-Tu-Asistente-Inteligente-para-Calificacion-de-Leads/
    cd LeadGenius-AI-Tu-Asistente-Inteligente-para-Calificacion-de-Leads
    ```

2.  **Instala las Dependencias:**
    ```bash
    pip install beautifulsoup4 requests pandas scikit-learn matplotlib seaborn
    ```

3.  **Configura tus Fuentes de Datos:**
    * **Web Scraping (`scraping_web.py`):**
        * Edita `scraping_web.py` y **cambia la `url_a_raspar`** por la URL del sitio web real que deseas monitorear.
        * **Ajusta la lógica de extracción (`soup.find_all`)** para que coincida con la estructura HTML del sitio elegido (usa las herramientas de desarrollador de tu navegador para inspeccionar los elementos).
    * **Otras Fuentes (`ingesta_otras_fuentes.py`):**
        * Crea un archivo `leads_evento.csv` en la misma carpeta con datos de ejemplo (o tus propios datos de eventos/ferias).
        * Edita el script para simular la ingesta de formularios de contacto si lo deseas.

4.  **Ejecuta el Flujo Completo (Orden Recomendado):**
    Puedes ejecutar cada script individualmente o usar el script `ejecutar_todo.py` para un ciclo completo:

    ```bash
    # Ejecutar uno a uno
    python scraping_web.py
    python ingesta_otras_fuentes.py
    python modelo_calificacion.py
    python calificar_leads.py
    python dashboard_bi.py
    ```
    O usa el script maestro:
    ```bash
    python ejecutar_todo.py
    ```

5.  **Configura las Alertas por Email:**
    * Edita `dashboard_bi.py` y **configura tus credenciales de email** (`sender_email`, `sender_password`, `receiver_email`) en la función `enviar_alerta_leads_altos`.
    * **Importante:** Si usas Gmail, genera una "contraseña de aplicación" en tu cuenta de Google.

---

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar LeadGenius AI, optimizar el scraping, mejorar los modelos de ML o añadir nuevas funcionalidades, por favor, abre un "issue" o envía un "pull request".

---

---

**¡Empieza a identificar tus próximos clientes exitosos hoy mismo con LeadGenius AI!**

