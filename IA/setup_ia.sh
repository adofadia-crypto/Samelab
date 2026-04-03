cat << 'EOF' > IA/setup_ia.sh
#!/bin/bash

# 1. Navegar a la carpeta de IA
cd /home/site/wwwroot/IA || exit

# 2. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "--- Creando entorno virtual (venv) ---"
    python3 -m venv venv
fi

# 3. Activar el entorno
source venv/bin/activate

# 4. Instalar dependencias desde el archivo de requerimientos
if [ -f "requirements.txt" ]; then
    echo "--- Instalando librerías desde requirements.txt ---"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "--- [AVISO] No se encontró requirements.txt, instalando básicas ---"
    pip install pandas numpy joblib sqlalchemy pyodbc
fi

echo "--- [ÉXITO] Configuración de IA completada ---"
EOF