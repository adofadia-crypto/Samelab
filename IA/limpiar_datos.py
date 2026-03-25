import pandas as pd
import sys
from db_config import obtener_engine # Tu llave maestra
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_limpieza():
    print("\n" + "="*40)
    print("--- [PASO 1] INICIANDO LIMPIEZA DE DATOS ---")
    print("="*40)

    try:
        # Aquí ya no necesitas poner server ni password, db_config lo hace por ti
        engine = obtener_engine()
        if not engine:
            print("--- [ERROR] No se pudo conectar a la base de datos ---")
            return
            
        # Añade esto para debuggear:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        print(f"--- [DEBUG] Tablas detectadas: {inspector.get_table_names()} ---")

        print("--- [PASO 3] Cargando tabla 'empleados' desde Azure ---")
        df = pd.read_sql("SELECT * FROM empleados", engine)
        
        if df.empty:
            print("--- [AVISO] La tabla origen está vacía ---")
            return

        # --- [PASO 4] Tu lógica de limpieza (Se queda exactamente igual) ---
        print("--- [PASO 4] Procesando limpieza y transformación ---")
        df_limpio = df.copy() 
        
        # Aquí puedes agregar df_limpio.fillna(0) si ves que hay nulos, pero si así te funciona, déjalo así.

        print(f"--- [PASO 5] Guardando {len(df_limpio)} registros limpios ---")
        # 'replace' asegura que la tabla siempre esté fresca para la IA
        df_limpio.to_sql('empleados_limpios', con=engine, if_exists='replace', index=False)
        
        print("="*40)
        print("--- [EXITO] Datos listos para la IA ---")
        print("="*40)

    except Exception as e:
        print(f"\n!!! ERROR EN LIMPIEZA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_limpieza()