import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_limpieza():
    print("\n" + "="*40)
    print("--- [PASO 1] INICIANDO LIMPIEZA DE DATOS ---")
    print("="*40)

    try:
        # CONFIGURACIÓN (REEMPLAZA ESTO)
        server = 'samelab-sql-server.database.windows.net'
        database = 'samelab_db'
        username = 'adolfo_admin'
        password = 'ChoforoMysql26#$'
        
        params = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        
        print("--- [PASO 2] Conectando a la Base de Datos ---")
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
        print("--- [PASO 3] Cargando tabla 'empleados' ---")
        df = pd.read_sql("SELECT * FROM empleados", engine)
        
        if df.empty:
            print("--- [AVISO] La tabla origen está vacía ---")
            return

        # --- [PASO 4] Lógica de limpieza ---
        print("--- [PASO 4] Procesando limpieza y transformación ---")
        # Aquí puedes añadir tus transformaciones (ej. df.fillna(0))
        df_limpio = df.copy() 
        
        print(f"--- [PASO 5] Guardando {len(df_limpio)} registros limpios ---")
        df_limpio.to_sql('empleados_limpios', con=engine, if_exists='replace', index=False)
        
        print("="*40)
        print("--- [EXITO] Datos listos para la IA ---")
        print("="*40)

    except Exception as e:
        print(f"\n!!! ERROR EN LIMPIEZA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_limpieza()