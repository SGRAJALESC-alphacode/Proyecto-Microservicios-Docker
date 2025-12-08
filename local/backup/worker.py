import time
import json
import os
import mysql.connector
from datetime import datetime

# Configuración (Variables de entorno)
DB_CONFIG = {
    'host': os.environ.get('CLOUD_DB_HOST'),
    'port': os.environ.get('CLOUD_DB_PORT'),
    'user': os.environ.get('CLOUD_DB_USER'),
    'password': os.environ.get('CLOUD_DB_PASSWORD'),
    'database': os.environ.get('CLOUD_DB_NAME')
}

BACKUP_DIR = "/backups"
INTERVAL = int(os.environ.get('SYNC_INTERVAL', 600)) 

def perform_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Iniciando respaldo...", flush=True)
    
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # --- LA SOLUCIÓN: Formatear la fecha directamente en SQL ---
        query = """
            SELECT 
                id, 
                ciudad, 
                temperatura, 
                humedad, 
                DATE_FORMAT(fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro 
            FROM mediciones
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Guardar en archivo JSON
        # Usamos el timestamp actual para el nombre del archivo
        filename = f"{BACKUP_DIR}/backup_{int(time.time())}.json"
        
        with open(filename, 'w') as f:
            json.dump(rows, f, indent=4)
            
        print(f"Respaldo exitoso: {len(rows)} registros guardados en {filename}", flush=True)
        
        cursor.close()
        
    except Exception as e:
        print(f"Error en el respaldo: {e}", flush=True)
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("--- Worker de Respaldo Iniciado (Formato Sincronizado) ---", flush=True)
    # Espera inicial para dar tiempo a que la BD arranque
    time.sleep(5) 
    while True:
        perform_backup()
        print(f"Esperando {INTERVAL} segundos para el siguiente ciclo...", flush=True)
        time.sleep(INTERVAL)