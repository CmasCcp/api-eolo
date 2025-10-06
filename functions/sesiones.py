from datetime import datetime
from flask import Blueprint, request, jsonify
import pymysql
import os
import json
import requests
# from dotenv import load_dotenv

# load_dotenv(dotenv_path="/var/www/api-eolo/.env")


# Configuración del directorio para guardar los archivos
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
JSON_FILES_ROOT = os.getenv("JSON_FILES_ROOT")
JSON_FILES_API_SENSORES_ROOT = os.getenv("JSON_FILES_API_SENSORES_ROOT")
JSON_FILES_USER_ROOT = os.getenv("JSON_FILES_USER_ROOT")
JSON_FILES_SESIONES_JSON = os.getenv("JSON_FILES_SESIONES_JSON")
API_SENSORES_ROOT = os.getenv("API_SENSORES_ROOT")



sesiones_bp = Blueprint('sesiones', __name__)


# Endpoint GET para leer los datos de 'sesiones.json'
@sesiones_bp.route('/sesiones', methods=['GET'])
def get_sessions():
    print(JSON_FILES_API_SENSORES_ROOT+"/sesiones.json")
    if os.path.exists(JSON_FILES_API_SENSORES_ROOT+"/sesiones.json"):
        with open(JSON_FILES_API_SENSORES_ROOT+"/sesiones.json", 'r', encoding='utf-8') as file:
            data = json.load(file)  # Leer el archivo JSON
        return jsonify(data), 200  # Devolver los datos como JSON
    else:
        return jsonify({"error": "El archivo sesiones.json no existe"}), 404

# Endpoint GET para leer los datos de 'sesiones.json'
@sesiones_bp.route('/sesion', methods=['GET'])
def get_sesion():
    patente = request.args.get('id_sesion')
    if not patente:
        return jsonify({"error": "Falta el parámetro 'patente'"}), 400
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = "SELECT * FROM sesiones WHERE id_sesion = %s"
            cursor.execute(sql, (patente))
            sesiones = cursor.fetchall()

        connection.close()
        return jsonify(sesiones), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener sesiones: {str(e)}"}), 500

# Endpoint GET para leer los datos de 'sesiones.json'
@sesiones_bp.route('/mis-sesiones', methods=['GET'])
def get_my_sessions():
    patente = request.args.get('patente')
    if not patente:
        return jsonify({"error": "Falta el parámetro 'patente'"}), 400
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = "SELECT * FROM sesiones WHERE patente = %s"
            cursor.execute(sql, (patente))
            sesiones = cursor.fetchall()

        connection.close()
        return jsonify(sesiones), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener sesiones: {str(e)}"}), 500




# Endpoint para agregar una nueva sesión
@sesiones_bp.route('/add-session', methods=['POST'])
def add_session():
    try:
        # Obtener los datos de la nueva sesión desde la solicitud
        new_session = request.get_json()

         # Agregar el encabezado User-Agent para evitar el bloqueo
        headers = {
            'User-Agent': 'EOLO/1.0 (dkressing@udd.cl)'  # Agrega un correo válido o información relevante
        }

        # Solicitar a la API de Nominatim
        response = requests.get(f'https://nominatim.openstreetmap.org/reverse', 
                                params={'lat': new_session["lat"],"lon": new_session["lon"], 'format': 'json'},
                                headers=headers)

        data_location = response.json()
        location_display_name = data_location["display_name"]
        address = data_location["address"]
        new_session["ubicacion"] = location_display_name
        new_session["ubicacion_corto"] = address.get("city", "") or address.get("road", "") or address.get("suburb", "") or address.get("county", "")
        
        required_fields = ['ubicacion', "ubicacion_corto","lat", "lon", 'filename', 'patente', 'volumen', 'fecha_inicial','fecha_final']
        
        
        if not all(field in new_session for field in required_fields):
            return jsonify({"error": "Faltan campos requeridos"}), 400
     
        try:
            # --- GUARDAR sesion EN MYSQL ---
            connection = pymysql.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO sesiones (
                        filename, patente, ubicacion_corto, lat, lon,
                        timestamp_inicial,timestamp_final, volumen, flujo, bateria
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    new_session['filename'],
                    new_session['patente'],
                    new_session['ubicacion_corto'],
                    new_session['lat'],
                    new_session['lon'],
                    new_session['fecha_inicial'],
                    new_session['fecha_final'],
                    new_session['volumen'],
                    new_session['flujo'],
                    new_session['bateria']
                ))


                # TODO: Obtener el ID de la sesión recién insertada (esta es una buena forma de asignar el id? que pasa si varias personas suben sesiones al mismo tiempo?)
                cursor.execute("SELECT LAST_INSERT_ID() as id")
                id_sesion = cursor.fetchone()['id']

            connection.commit()
            connection.close()

            # --- NUEVO: Insertar datos del archivo JSON en la tabla datos ---
            json_path = JSON_FILES_SESIONES_JSON + f"/{new_session['filename']}.json"
            res = insert_mediciones_from_json(json_path,new_session['patente'], API_SENSORES_ROOT + "/insertarMedicionV2", new_session)
            # print(res)
            # if os.path.exists(json_path):
        except Exception as e:
            return jsonify({"error": f"Hubo un problema al guardar la sesión en la base de datos: {str(e)}"}), 500                


        return jsonify({"message": "Sesión agregada exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Hubo un problema al agregar la sesión: {str(e)}"}), 500

# Utilidad para hacer petición GET a la API de sensores usando los datos de un JSON
def insert_mediciones_from_json(json_path, patente,api_url, newSession):
    """
    Lee un archivo JSON y realiza una petición GET a la API de sensores
    usando los datos del JSON como parámetros. Retorna una lista con las respuestas.
    """
    if not os.path.exists(json_path):
        return {"error": f"El archivo {json_path} no existe"}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        rows = data if isinstance(data, list) else [data]
        results = []
        for idx, row in enumerate(rows, start=1):
            timestamp = row.get("timestamp", "")
            velocidad = row.get("velocidad_valor", "")
            direccion = row.get("direccion_valor", "")
            temperatura = row.get("temperatura_valor", "")
            humedad = row.get("humedad_valor", "")
            pm1 = row.get("pm1_valor", "")
            pm2_5 = row.get("pm2.5_valor", "")
            pm10 = row.get("pm10_valor", "")
            presion = row.get("presion_valor", "")
            flujo = row.get("flujo_valor", "")
            volumen = row.get("volumen_valor", "")
            voltaje = row.get("bateria_valor", "")
            latitud = newSession.get("lat", "")
            longitud = newSession.get("lon", "")
            intensidad_senal = "100" # TODO: de donde viene este dato? estara en el mpe?
            satelites = "100"
            # TODO: diferenciar las variables que se repiten (temperatura, humedad, flujo)
            # valores = f"{Velocidad del viento [m/s]},{Dirección del Viento [Grados]},{Grados celcius [°C]},{Humedad [%]},{Material particulado PM 1.0 [µg/m³]},{Material particulado PM 2.5 [µg/m³]},{Material particulado PM 10 [µg/m³]},{Grados celcius [°C]},{Humedad [%]},{Presión atmosférica [kPa]},{Flujo de captura configurado [L/min]},{Volumen capturado [m3]},{Flujo de captura observado [L/min]},{Grados celcius [°C]},{Voltaje [V]},{Latitud [°]},{Longitud [°]},{Intensidad señal telefónica [Adimensional]},{Velocidad_km/h [km/h]},{Satelites [int]}"
            valores = f"{velocidad},{direccion},{temperatura},{humedad},{pm1},{pm2_5},{pm10},{temperatura},{humedad},{presion},{flujo},{volumen},{flujo},{temperatura},{voltaje},{latitud},{longitud},{intensidad_senal},{velocidad},{satelites}"
            # valores=8.79999999999999,44,15,30,,14.0,20.22,15,30,1050,12,180,12,15,5,,,100,8.79999999999999,100
            params = f"?times={timestamp}&codigoInterno={patente}&idsSensorTipo=37,37,6,6,6,6,6,8,8,8,38,38,38,27,4,13,13,13,13,13&idsVariables=5,17,3,6,7,8,9,3,6,13,48,49,50,3,4,11,12,15,45,46&valores=" + valores

            headers = {'User-Agent': 'EOLO/1.0 (dkressing@udd.cl)'}
            response = requests.get(api_url+params, headers=headers)
            try:
                print(f"Simulando petición a {api_url} con params: {params}")
                results.append(response.json())
            except Exception:
                print("Error procesando fila", idx)
                
                results.append({"error": "Respuesta no es JSON", "status_code": response.status_code, "text": response.text})
        return results
        # return {"message": "Mediciones insertadas (simulado)"}
    except Exception as e:
        return {"error": str(e)}