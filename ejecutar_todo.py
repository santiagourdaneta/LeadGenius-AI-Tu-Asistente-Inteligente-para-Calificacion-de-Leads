# Archivo: ejecutar_todo.py
import subprocess
import time

def run_script(script_name):
    print(f"\n--- Ejecutando {script_name} ---")
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errores en {script_name}:\n{result.stderr}")
    print(f"--- Finalizado {script_name} ---")
    time.sleep(1) # Pequeña pausa

if __name__ == "__main__":
    # Orden de ejecución para un ciclo completo
    run_script('scraping_web.py')
    run_script('ingesta_otras_fuentes.py')
    
    # Después de recolectar nuevos datos, re-entrenamos y calificamos
    # En producción, el re-entrenamiento no sería diario, quizás semanal o mensual.
    # Por simplicidad aquí lo incluimos.
    run_script('modelo_calificacion.py') 
    
    run_script('calificar_leads.py')
    run_script('dashboard_bi.py')
    
    print("\n¡Ciclo completo de procesamiento de leads finalizado!")