from flask import Flask, render_template, jsonify
import mysql.connector
import os
import requests
import concurrent.futures
import random  # Necesario para elegir ciudad al azar

app = Flask(__name__)

# Configuración de conexión a Nube
DB_CONFIG = {
    'host': os.environ.get('CLOUD_DB_HOST'),
    'port': os.environ.get('CLOUD_DB_PORT'),
    'user': os.environ.get('CLOUD_DB_USER'),
    'password': os.environ.get('CLOUD_DB_PASSWORD'),
    'database': os.environ.get('CLOUD_DB_NAME')
}

# --- COORDENADAS DE CIUDADES COLOMBIANAS ---
CITIES_COORDS = [
    {"name": "Manizales, CO", "lat": 5.07, "lon": -75.51},
    {"name": "Bogota, CO",    "lat": 4.71, "lon": -74.07},
    {"name": "Medellin, CO",  "lat": 6.24, "lon": -75.58},
    {"name": "Cali, CO",      "lat": 3.45, "lon": -76.53},
    {"name": "Cartagena, CO", "lat": 10.39, "lon": -75.48},
    {"name": "Pereira, CO",   "lat": 4.81, "lon": -75.69},
    {"name": "Bucaramanga, CO", "lat": 7.11, "lon": -73.12}
]

# Función auxiliar para consultar la API (Se ejecuta en un hilo aparte)
def fetch_weather_api(city_data):
    # Construimos la URL dinámica con las coordenadas de la ciudad elegida
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city_data['lat']}&longitude={city_data['lon']}&current_weather=true"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        # Le inyectamos el nombre de la ciudad para mostrarlo en el front
        data['city_name'] = city_data['name']
        return data
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint Botón 1: API Externa (Ahora es DINÁMICO)
@app.route('/get-external-data')
def get_external_data():
    # 1. Elegimos una ciudad al azar de nuestra lista
    selected_city = random.choice(CITIES_COORDS)

    # 2. Usamos Concurrencia (ThreadPool) para consultar la API
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    future = executor.submit(fetch_weather_api, selected_city)
    data = future.result()
    
    # 3. Devolvemos el JSON al navegador
    return jsonify({
        "source": "API Pública (Open-Meteo)",
        "location": data.get('city_name', 'Desconocido'),
        "temperature": data.get('current_weather', {}).get('temperature', 'N/A'),
        "windspeed": data.get('current_weather', {}).get('windspeed', 'N/A')
    })

# Endpoint Botón 2: Base de Datos Nube (Ya está perfecto)
@app.route('/get-cloud-data')
def get_cloud_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                id, 
                ciudad, 
                temperatura, 
                humedad, 
                DATE_FORMAT(fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro 
            FROM mediciones 
            ORDER BY fecha_registro DESC 
            LIMIT 5
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": f"Error conectando a la Nube: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)