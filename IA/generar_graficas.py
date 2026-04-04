import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from db_config import obtener_engine

def generar_reporte_visual():
    engine = obtener_engine()
    if engine is None: return

    # 1. Cargar datos de la capa de ORO
    query = "SELECT * FROM empleados_visualizacion"
    df = pd.read_sql(query, engine)

    # Configuración de estilo
    sns.set_theme(style="whitegrid")
    
    # Ruta de salida (Ajustada para Azure y Local)
    # Buscamos la carpeta wwwroot/images
    base_path = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(base_path, "..", "wwwroot", "images")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # --- GRÁFICA 1: Impacto por Departamento ---
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Department', hue='RiskLevel', palette='viridis')
    plt.title('Distribución de Riesgo por Departamento')
    plt.savefig(os.path.join(output_folder, "grafica_depto.png"), bbox_inches='tight')
    plt.close()

    # --- GRÁFICA 2: Riesgo por Probabilidad (Histograma) ---
    # Nota: Como no tenemos 'Age' en la tabla de visualización, 
    # usaremos la Probabilidad de Attrition que es muy visual
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='AttritionProbability', kde=True, color='skyblue')
    plt.title('Densidad de Probabilidad de Abandono')
    plt.savefig(os.path.join(output_folder, "grafica_edad.png"), bbox_inches='tight')
    plt.close()

    # --- GRÁFICA 3: Satisfacción vs Riesgo ---
    plt.figure(figsize=(12, 5))
    # Simulamos una densidad basada en JobRole y Risk
    sns.boxplot(data=df, x='RiskLevel', y='AttritionProbability', palette='magma')
    plt.title('Análisis de Probabilidad por Nivel de Riesgo')
    plt.savefig(os.path.join(output_folder, "grafica_satisfaccion.png"), bbox_inches='tight')
    plt.close()

    print("--- [ÉXITO] Gráficas exportadas a wwwroot/images ---")

if __name__ == "__main__":
    generar_reporte_visual()