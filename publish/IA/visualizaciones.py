import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector

# Conexión a tu MAMP
conn = mysql.connector.connect(
    user='root', password='root', host='localhost', port='8889', database='samelab_db'
)
df = pd.read_sql("SELECT * FROM empleados", conn)

# --- GRÁFICA 1: Distribución de Attrition ---
plt.figure(figsize=(8, 6))
sns.countplot(x='Attrition', data=df, palette='viridis')
plt.title('Distribución de Rotación (Attrition)')
plt.savefig('IA/grafica_distribucion.png') # Se guarda como imagen
plt.show()

# --- GRÁFICA 2: Edad vs Attrition ---
plt.figure(figsize=(10, 6))
sns.boxplot(x='Attrition', y='Age', data=df)
plt.title('Relación entre Edad y Rotación')
plt.savefig('IA/grafica_edad.png')