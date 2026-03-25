import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_graficas():
    print("\n" + "="*40)
    print("--- [PASO 1] GENERANDO GRÁFICAS ---")
    print("="*40)

    try:
        # CONFIGURACIÓN (REEMPLAZA ESTO)
        server = 'samelab-sql-server.database.windows.net'
        database = 'samelab_db'
        username = 'adolfo_admin'
        password = 'ChoforoMysql26#$'
        
        params = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
        print("--- [PASO 2] Leyendo resultados de predicción ---")
        df = pd.read_sql("SELECT * FROM empleados_visualizacion", engine)

        if df.empty:
            print("--- [ERROR] No hay datos en 'empleados_visualizacion' para graficar ---")
            return

        print("--- [PASO 3] Creando visualización con Seaborn ---")
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))
        
        # Ajusta 'Prediccion' al nombre de tu columna de resultados
        sns.countplot(data=df, x='Prediccion', palette='viridis')
        plt.title('Distribución de Resultados de la IA', fontsize=15)
        plt.xlabel('Categoría', fontsize=12)
        plt.ylabel('Cantidad de Empleados', fontsize=12)

        # RUTA DE GUARDADO: Muy importante para Azure
        # Usamos /home/site/wwwroot/wwwroot/images/ o similar
        output_dir = os.path.join(os.getcwd(), "wwwroot", "images")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"--- Carpeta creada: {output_dir} ---")

        file_name = "grafica_ia.png"
        path_final = os.path.join(output_dir, file_name)
        
        plt.savefig(path_final, bbox_inches='tight')
        plt.close()
        
        print(f"--- [EXITO] Gráfica guardada en: {path_final} ---")
        print("="*40)

    except Exception as e:
        print(f"\n!!! ERROR AL GRAFICAR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_graficas()