import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from db_config import obtener_engine # Tu conexión centralizada
import warnings

# Silenciamos avisos para que la consola de Azure se vea limpia
warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_graficas():
    print("\n" + "="*40)
    print("--- [PASO 1] GENERANDO GRÁFICAS ---")
    print("="*40)

    try:
        # 1. Conexión automática desde appsettings.json
        engine = obtener_engine()
        if not engine:
            print("--- [ERROR] No se pudo establecer conexión para graficar ---")
            return
    
        # 2. Lectura de datos finales
        print("--- [PASO 2] Leyendo resultados de predicción ---")
        df = pd.read_sql("SELECT * FROM empleados_visualizacion", engine)

        if df.empty:
            print("--- [ERROR] No hay datos en 'empleados_visualizacion' para graficar ---")
            return

        # 3. Configuración de la visualización
        print("--- [PASO 3] Creando visualización con Seaborn ---")
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))
        
        # Generamos la gráfica de barras con los resultados (Sí/No)
        sns.countplot(data=df, x='Prediccion', palette='viridis')
        plt.title('Distribución de Resultados de la IA (Samelab)', fontsize=15)
        plt.xlabel('Predicción de Attrition', fontsize=12)
        plt.ylabel('Cantidad de Empleados', fontsize=12)

        # 4. Manejo de Rutas para Azure y Local
        # Importante: Buscamos la carpeta wwwroot/images relativa a la ejecución del Controller
        output_dir = os.path.join(os.getcwd(), "wwwroot", "images")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"--- Carpeta creada: {output_dir} ---")

        path_final = os.path.join(output_dir, "grafica_ia.png")
        
        # Guardamos y cerramos para liberar memoria
        plt.savefig(path_final, bbox_inches='tight')
        plt.close()
        
        print(f"--- [EXITO] Gráfica guardada en: {path_final} ---")
        print("="*40)

    except Exception as e:
        print(f"\n!!! ERROR AL GRAFICAR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_graficas()