import pandas as pd
import joblib
import os
import sys
import numpy as np
from db_config import obtener_engine
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def ejecutar_prediccion():
    print("\n" + "="*40)
    print("--- [PASO 2] PREDICCIÓN IA (PLATA -> ORO) ---")
    print("="*40)

    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_path, 'modelo_logistico_samelab.pkl')
        
        if not os.path.exists(model_path):
            print(f"!!! ERROR: No se encuentra el modelo en {model_path}")
            return
            
        modelo = joblib.load(model_path)
        engine = obtener_engine()
        
        # 1. LEER DE LA TABLA LIMPIA
        df_original = pd.read_sql("SELECT * FROM empleados_limpios", engine)
        
        if df_original.empty:
            print("--- [AVISO] No hay datos limpios para procesar ---")
            return

        # 2. Preparar entrada para el modelo
        df_input = df_original.drop(columns=['Attrition'], errors='ignore')
        df_input = pd.get_dummies(df_input)

        # Alineación de columnas con el modelo
        model_features = modelo.feature_names_in_
        for col in model_features:
            if col not in df_input.columns:
                df_input[col] = 0
        df_input = df_input[model_features]

        # 3. EJECUTAR MODELO
        print("--- [PROCESANDO] Calculando Probabilidades ---")
        
        # Guardamos los resultados directamente en el DataFrame original
        df_original['PredictedAttrition'] = modelo.predict(df_input)
        probs = modelo.predict_proba(df_input)[:, 1]
        df_original['AttritionProbability'] = probs

        # 4. CLASIFICACIÓN DE RIESGO (SEMÁFORO)
        conditions = [
            (df_original['AttritionProbability'] <= 0.3),
            (df_original['AttritionProbability'] > 0.3) & (df_original['AttritionProbability'] <= 0.7),
            (df_original['AttritionProbability'] > 0.7)
        ]
        choices = ['Low', 'Medium', 'High']
        df_original['RiskLevel'] = np.select(conditions, choices, default='Low')

        # 5. GUARDAR EN TABLA DE VISUALIZACIÓN (ORO)
        # Aquí NO creamos la columna 'Prediccion', usamos 'RiskLevel'
        print("--- [PASO 3] Generando tabla 'empleados_visualizacion' ---")
        df_original.to_sql('empleados_visualizacion', con=engine, if_exists='replace', index=False)
        
        print("="*40)
        print(f"--- [ÉXITO] Resultados generados correctamente ---")
        print("="*40)

    except Exception as e:
        print(f"\n--- [ERROR CRÍTICO] : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_prediccion()