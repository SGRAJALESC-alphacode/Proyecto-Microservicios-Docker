import time
import random
import os
import mysql.connector
import requests  # Nueva librería para consultar internet
from datetime import datetime

# Configuración de base de datos
DB_CONFIG = {
    'host': os.environ.get('CLOUD_DB_HOST'),
    'port': os.environ.get('CLOUD_DB_PORT'),
    'user': os.environ.get('CLOUD_DB_USER'),
    'password': os.environ.get('CLOUD_DB_PASSWORD'),
    'database': os.environ.get('CLOUD_DB_NAME')
}

# --- COORDENADAS REALES (Misma lógica que el Frontend) ---
CITIES_DATA = [
    {"name": "Manizales", "lat": 5.07, "lon": -75.51},
    {"name": "Bogota",    "lat": 4.71, "lon": -74.07},
    {"name": "Medellin",  "lat": 6.24, "lon": -75.58},
    {"name": "Cali",      "lat": 3.45, "lon": -76.53},
    {"name": "Cartagena", "lat": 10.39, "lon": -75.48},
    {"name": "Pereira",   "lat": 4.81, "lon": -75.69},
    {"name": "Bucaramanga", "lat": 7.11, "lon": -73.12}
]

def get_real_weather(lat, lon):
    """Consulta la API de Open-Meteo para obtener datos reales"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "temp": data['current_weather']['temperature'],
            "wind": data['current_weather']['windspeed']
        }
    except Exception as e:
        print(f"Error consultando API: {e}")
        # Valor de respaldo por si falla internet
        return {"temp": 20.0, "wind": 5.0}

def simulate_sensor():
    print("--- Iniciando Sensor IoT con Datos REALES ---", flush=True)
    
    while True:
        try:
            # 1. Elegir ciudad al azar
            city_info = random.choice(CITIES_DATA)
            
            # 2. Consultar el clima REAL de esa ciudad
            real_data = get_real_weather(city_info['lat'], city_info['lon'])
            
            # 3. Usamos la temperatura real (y simulamos humedad basada en algo aleatorio realista)
            temp = real_data['temp']
            hum = random.randint(40, 95) 
            
            # 4. Conectar a la Nube e Insertar
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            query = "INSERT INTO mediciones (ciudad, temperatura, humedad) VALUES (%s, %s, %s)"
            cursor.execute(query, (city_info['name'], temp, hum))
            conn.commit()
            
            print(f"[{datetime.now()}] 📡 Datos REALES enviados desde {city_info['name']}: {temp}°C", flush=True)
            
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error crítico: {e}", flush=True)

        # Esperar 15 segundos exactos
        time.sleep(15)

if __name__ == "__main__":
    time.sleep(5)
    simulate_sensor()