import pandas as pd
import sys
from db_config import obtener_engine
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_limpieza():
    print("\n" + "="*40)
    print("--- [PASO 1] LIMPIEZA DE DATOS (BRONCE -> PLATA) ---")
    print("="*40)

    try:
        engine = obtener_engine()
        if not engine:
            print("!!! ERROR: No se pudo conectar a Azure SQL.")
            return
            
        # 1. Leer datos crudos
        df = pd.read_sql("SELECT * FROM empleados", engine)
        
        if df.empty:
            print("--- [AVISO] Tabla 'empleados' vacía. Sube un CSV primero.")
            return

        # 2. Proceso de Limpieza
        df_limpio = df.copy()

        # Eliminamos cualquier columna de resultados previa si existiera por error
        columnas_resultados = ['PredictedAttrition', 'AttritionProbability', 'RiskLevel', 'Prediccion']
        df_limpio = df_limpio.drop(columns=[col for col in columnas_resultados if col in df_limpio.columns], errors='ignore')

        # Manejo de nulos básico
        df_limpio = df_limpio.fillna(0)

        # 3. Guardar en la tabla de entrenamiento/predicción (Plata)
        print("--- [PASO 2] Guardando en 'empleados_limpios' ---")
        df_limpio.to_sql('empleados_limpios', con=engine, if_exists='replace', index=False)
        
        print("="*40)
        print(f"--- [ÉXITO] Datos listos para la IA ---")
        print("="*40)

    except Exception as e:
        print(f"\n!!! ERROR EN LIMPIEZA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_limpieza()