import pandas as pd
import joblib
from sqlalchemy import create_engine
import os
import sys
import warnings

# 1. Silenciar avisos
warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_prediccion():
    print("\n" + "="*40)
    print("--- [PASO 1] INICIANDO SCRIPT DE PREDICCIÓN ---")
    print("="*40)

    try:
        # 2. Rutas y Configuración
        base_path = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_path, 'modelo_logistico_samelab.pkl')
        
        # CREDENCIALES (Asegúrate de que sean las correctas)
        server = 'samelab-sql-server.database.windows.net'
        database = 'samelab_db'
        username = 'adolfo_admin'
        password = 'ChoforoMysql26#$'
        
        # 3. Carga del Modelo
        print(f"--- [PASO 2] Cargando modelo: {model_path} ---")
        modelo = joblib.load(model_path)
        
        # 4. Conexión con Driver Seguro
        print("--- [PASO 3] Conectando a Azure SQL ---")
        driver = 'ODBC Driver 17 for SQL Server'
        if os.path.exists('/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.so'):
            driver = '/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.so'
            
        params = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
        # 5. Leer datos
        print("--- [PASO 4] Leyendo tabla 'empleados_limpios' ---")
        df_original = pd.read_sql("SELECT * FROM empleados_limpios", engine)
        
        if df_original.empty:
            print("--- [AVISO] Tabla vacía ---")
            return

        # 6. ALINEACIÓN DE COLUMNAS (El fix para el error)
        print(f"--- [PASO 5] Transformando {len(df_original)} registros ---")
        
        # Eliminamos la columna objetivo si existe en la entrada
        df_input = df_original.drop(columns=['Attrition'], errors='ignore')
        
        # Aplicamos One-Hot Encoding (pd.get_dummies)
        df_input = pd.get_dummies(df_input)

        # Obtenemos las columnas que el modelo "aprendió" en el entrenamiento
        # Scikit-learn guarda esto en feature_names_in_
        try:
            model_features = modelo.feature_names_in_
        except AttributeError:
            print("!!! Error: El modelo no tiene grabados los nombres de las columnas.")
            print("Asegúrate de que el modelo se entrenó con un DataFrame de Pandas.")
            sys.exit(1)

        # Añadimos las columnas que falten con valor 0
        for col in model_features:
            if col not in df_input.columns:
                df_input[col] = 0
        
        # Seleccionamos y reordenamos las columnas exactamente como las quiere el modelo
        df_input = df_input[model_features]

        # 7. Ejecutar Predicción
        print("--- [PASO 6] Ejecutando modelo logístico ---")
        predicciones = modelo.predict(df_input)
        
        # Agregamos el resultado al DataFrame original para guardarlo
        df_original['Prediccion'] = predicciones
        
        # 8. Guardar Resultados
        print("--- [PASO 7] Guardando en 'empleados_visualizacion' ---")
        df_original.to_sql('empleados_visualizacion', con=engine, if_exists='replace', index=False)
        
        print("="*40)
        print(f"--- [EXITO TOTAL] {len(df_original)} predicciones generadas ---")
        print("="*40)

    except Exception as e:
        print(f"\n--- [ERROR CRÍTICO] ---")
        print(f"Detalle: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_prediccion()