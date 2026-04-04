#!/bin/bash

# 1. Ir a la carpeta de trabajo
cd /home/site/wwwroot/IA || exit

echo "--- [PASO 1] Configurando Drivers de Microsoft SQL ---"
# Intentamos correr tu script de drivers. 
# Nota: Si falla por permisos, el script seguirá adelante gracias al '|| true'
{
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft-archive-keyring.gpg 2>/dev/null
    echo "deb [arch=amd64,arm64,armhf] https://packages.microsoft.com/debian/12/prod bookworm main" > mssql-release.list
    # En Azure App Service no solemos tener apt-get, pero lo intentamos por si tu plan lo permite
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
} || echo "Aviso: No se pudieron instalar drivers de sistema (falta sudo), usando drivers preinstalados."

echo "--- [PASO 2] Instalando PIP (Rescate) ---"
# Si no hay pip, lo bajamos manualmente
if ! python3 -m pip --version > /dev/null 2>&1; then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# 3. Exportar rutas para que Python encuentre los paquetes de usuario
export PATH=$PATH:/home/site/.local/bin
export PYTHONPATH=$PYTHONPATH:/home/site/.local/lib/python3.11/site-packages

echo "--- [PASO 3] Instalando librerías de IA ---"
python3 -m pip install --user --upgrade pip
if [ -f "requirements.txt" ]; then
    python3 -m pip install --user -r requirements.txt
else
    python3 -m pip install --user pandas numpy joblib sqlalchemy pyodbc
fi

echo "--- [ÉXITO] Entorno listo ---"