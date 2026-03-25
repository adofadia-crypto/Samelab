import os
import json
import urllib
import platform
import re
from sqlalchemy import create_engine

def obtener_engine():
    try:
        # 1. Localizar appsettings.json
        ruta_final = os.path.join(os.getcwd(), "appsettings.json")
        if not os.path.exists(ruta_final):
            ruta_final = os.path.join(os.getcwd(), "..", "appsettings.json")
        
        # 2. Leer credenciales
        with open(ruta_final, 'r') as f:
            config = json.load(f)
        
        raw_conn_str = config['ConnectionStrings']['DefaultConnection']

        # 3. EXTRAER CREDENCIALES (Ajustado)
        def buscar(patron, cadena):
            res = re.search(patron, cadena, re.IGNORECASE)
            return res.group(1) if res else ""

        server = buscar(r"Server=([^;]+)", raw_conn_str).replace("tcp:", "")
        user = buscar(r"(?:User Id|Uid)=([^;]+)", raw_conn_str)
        password = buscar(r"(?:Password|Pwd)=([^;]+)", raw_conn_str)
        
        # FORZAMOS EL NOMBRE DE LA BD YA QUE EL BUSCADOR NO LO ENCONTRÓ
        database = "samelab_db" 

        # 4. CONFIGURAR DRIVER SEGÚN MAC O AZURE
        sistema = platform.system()
        driver = "{ODBC Driver 17 for SQL Server}"
        
        if sistema == "Darwin": # Tu Mac
            driver_path = "/opt/homebrew/lib/libmsodbcsql.17.dylib"
            if os.path.exists(driver_path):
                driver = f"{{{driver_path}}}"

        # 5. CONSTRUIR CADENA FINAL PERFECTA
        conn_str = (
            f"Driver={driver};"
            f"Server={server};"
            f"Database={database};"
            f"Uid={user};"
            f"Pwd={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
        )

        print(f"--- [DEBUG LOCAL] Conectando a: {server} | BD: {database} ---")
        
        params = urllib.parse.quote_plus(conn_str)
        return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    except Exception as e:
        print(f"--- [ERROR] --- \nDetalle: {e}")
        return None