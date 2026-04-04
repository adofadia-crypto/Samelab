import os
import json
import re
import urllib.parse
from sqlalchemy import create_engine

def obtener_engine():
    try:
        # 1. En Azure, el appsettings.json está siempre en esta ruta
        ruta_config = "/home/site/wwwroot/appsettings.json"
        
        if not os.path.exists(ruta_config):
            # Fallback por si ejecutas localmente para pruebas rápidas
            ruta_config = os.path.join(os.getcwd(), "appsettings.json")

        with open(ruta_config, 'r') as f:
            config = json.load(f)
        
        # 2. Extraer la cadena de conexión de C#
        conn_str = config['ConnectionStrings']['DefaultConnection']

        # 3. Limpiar los datos para el formato de SQLAlchemy + pymssql
        # Buscamos: Server, User Id, Password y Database
        server = re.search(r"Server=([^;]+)", conn_str, re.I).group(1).replace("tcp:", "").split(",")[0]
        user = re.search(r"(?:User Id|Uid)=([^;]+)", conn_str, re.I).group(1)
        password = re.search(r"(?:Password|Pwd)=([^;]+)", conn_str, re.I).group(1)
        database = "samelab_db" # Nombre de tu DB en Azure

        # 4. Codificar el password (muy importante por si tiene caracteres raros)
        pass_encoded = urllib.parse.quote_plus(password)

        # 5. Crear el motor con el dialecto pymssql
        # Formato: mssql+pymssql://usuario:password@servidor/base_de_datos
        url_final = f"mssql+pymssql://{user}:{pass_encoded}@{server}/{database}?charset=utf8"
        
        print(f"--- [AZURE ENGINE] Conectando a {server} ---")
        return create_engine(url_final)

    except Exception as e:
        print(f"--- [ERROR AZURE ENGINE] --- \nDetalle: {e}")
        return None