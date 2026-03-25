import pandas as pd
import joblib
import os
import sys
from db_config import obtener_engine # Tu llave maestra centralizada
import warnings

# 1. Silenciar avisos de versiones de librerías
warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_prediccion():
    print("\n" + "="*40)
    print("--- [PASO 1] INICIANDO SCRIPT DE PREDICCIÓN ---")
    print("="*40)

    try:
        # 2. Rutas dinámicas para que funcione en Local y Azure
        base_path = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_path, 'modelo_logistico_samelab.pkl')
        
        # 3. Carga del Modelo Entrenado
        print(f"--- [PASO 2] Cargando modelo: {model_path} ---")
        if not os.path.exists(model_path):
            print(f"!!! ERROR: No se encuentra el archivo {model_path}")
            return
            
        modelo = joblib.load(model_path)
        
        # 4. Conexión usando el nuevo archivo centralizado
        print("--- [PASO 3] Conectando a Azure SQL ---")
        engine = obtener_engine()
        if not engine:
            return
        
        # 5. Leer datos limpios (producidos por limpiar_datos.py)
        print("--- [PASO 4] Leyendo tabla 'empleados_limpios' ---")
        df_original = pd.read_sql("SELECT * FROM empleados_limpios", engine)
        
        if df_original.empty:
            print("--- [AVISO] Tabla vacía, nada que predecir ---")
            return

        # 6. ALINEACIÓN DE COLUMNAS (Mantiene tu lógica intacta)
        print(f"--- [PASO 5] Transformando {len(df_original)} registros ---")
        
        # Preparamos los datos para el modelo
        df_input = df_original.drop(columns=['Attrition'], errors='ignore')
        df_input = pd.get_dummies(df_input)

        # Validación de columnas del modelo
        try:
            model_features = modelo.feature_names_in_
        except AttributeError:
            print("!!! Error: El modelo no reconoce las columnas. Revisa el entrenamiento.")
            sys.exit(1)

        # Rellenar columnas faltantes con 0 (One-Hot Encoding safe)
        for col in model_features:
            if col not in df_input.columns:
                df_input[col] = 0
        
        # Reordenar columnas según el entrenamiento del modelo
        df_input = df_input[model_features]

        # 7. Ejecutar Predicción
        print("--- [PASO 6] Ejecutando modelo logístico ---")
        predicciones = modelo.predict(df_input)
        
        # IMPORTANTE: Aquí es donde generamos el "Sí" o "No" para tu Index.cshtml
        # Si tu modelo escupe 1/0, esto lo convierte en el texto que espera tu tabla
        df_original['Prediccion'] = pd.Series(predicciones).apply(lambda x: "Sí" if x == 1 else "No")
        
        # 8. Guardar Resultados Finales
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