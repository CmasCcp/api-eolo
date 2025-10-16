from flask import Flask, request, jsonify
from flask_cors import CORS  # Importa CORS
import os
import json
from werkzeug.utils import secure_filename
import pandas as pd
import requests
from functions.cript import generate_pin
from dotenv import load_dotenv
import pymysql
from datetime import datetime
# Importar los blueprints de los módulos correspondientes
from functions.users import users_bp
from functions.dispositivos import dispositivos_bp
from functions.sesiones import sesiones_bp
from functions.datos import datos_bp


app = Flask(__name__)

# Habilitar CORS para permitir cualquier origen con configuración específica
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173","http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000", "https://eolo.cmasccp.cl", "http://eolo.cmasccp.cl"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True
    }
})

load_dotenv()

# Configuración del directorio para guardar los archivos
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
JSON_FILES_ROOT = os.getenv("JSON_FILES_ROOT")
JSON_FILES_API_SENSORES_ROOT = os.getenv("JSON_FILES_API_SENSORES_ROOT")
JSON_FILES_USER_ROOT = os.getenv("JSON_FILES_USER_ROOT")
JSON_FILES_SESIONES_JSON = os.getenv("JSON_FILES_SESIONES_JSON")


# --- GUARDAR EN MYSQL ---


# Asegúrate de que el directorio existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(users_bp)

app.register_blueprint(dispositivos_bp)

app.register_blueprint(sesiones_bp)

app.register_blueprint(datos_bp)


@app.route('/', methods=['GET'])
def api_documentation():
    """
    API Documentation endpoint that serves a comprehensive web page
    documenting all available endpoints
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EOLO API - Documentación</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: white;
                margin-top: 20px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border-radius: 10px;
                margin: -20px -20px 40px -20px;
            }
            
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .toc {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                border-left: 4px solid #667eea;
            }
            
            .toc h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .toc ul {
                list-style: none;
                padding-left: 0;
            }
            
            .toc li {
                margin-bottom: 8px;
            }
            
            .toc a {
                color: #333;
                text-decoration: none;
                padding: 5px 10px;
                border-radius: 4px;
                transition: all 0.3s;
                display: block;
            }
            
            .toc a:hover {
                background: #667eea;
                color: white;
            }
            
            .section {
                margin-bottom: 40px;
            }
            
            .section h2 {
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 2em;
            }
            
            .endpoint {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin-bottom: 20px;
                overflow: hidden;
                transition: all 0.3s;
            }
            
            .endpoint:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            
            .endpoint-header {
                background: #667eea;
                color: white;
                padding: 15px 20px;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .method {
                background: rgba(255,255,255,0.2);
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 0.9em;
                font-weight: bold;
            }
            
            .method.GET { background: #28a745; }
            .method.POST { background: #007bff; }
            .method.PUT { background: #ffc107; color: #000; }
            .method.DELETE { background: #dc3545; }
            
            .endpoint-body {
                padding: 20px;
            }
            
            .endpoint-description {
                margin-bottom: 15px;
                color: #666;
                font-style: italic;
            }
            
            .params, .response {
                margin-bottom: 15px;
            }
            
            .params h4, .response h4 {
                color: #495057;
                margin-bottom: 10px;
            }
            
            .param-list {
                background: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
            }
            
            .param {
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            
            .param:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            
            .param-name {
                font-weight: bold;
                color: #667eea;
            }
            
            .param-type {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.8em;
                margin-left: 8px;
            }
            
            .param-required {
                color: #dc3545;
                font-size: 0.8em;
                font-weight: bold;
                margin-left: 8px;
            }
            
            .example {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                overflow-x: auto;
                margin-top: 10px;
            }
            
            .base-url {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 30px;
                text-align: center;
                border: 2px solid #667eea;
            }
            
            .base-url code {
                background: #667eea;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 1.1em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌪️ EOLO API</h1>
                <p>Documentación completa de la API para el sistema de monitoreo ambiental EOLO</p>
            </div>
            
            <div class="base-url">
                <strong>URL Base:</strong> <code>http://127.0.0.1:5000</code>
            </div>
            
            <div class="toc">
                <h3>📋 Tabla de Contenidos</h3>
                <ul>
                    <li><a href="#auth">🔐 Autenticación</a></li>
                    <li><a href="#devices">📱 Dispositivos</a></li>
                    <li><a href="#sessions">📊 Sesiones</a></li>
                    <li><a href="#data">📈 Datos</a></li>
                    <li><a href="#utils">🔧 Utilidades</a></li>
                </ul>
            </div>
            
            <div class="section" id="auth">
                <h2>🔐 Autenticación</h2>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/login</span>
                        <span class="method POST">POST</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Autenticar un usuario en el sistema
                        </div>
                        <div class="params">
                            <h4>Parámetros (JSON Body):</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">username</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Nombre de usuario</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">password</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Contraseña del usuario</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Respuesta exitosa (200):</h4>
                            <div class="example">
{
    "message": "Login exitoso",
    "username": "usuario123",
    "id_usuario": 1
}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="devices">
                <h2>📱 Dispositivos</h2>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/dispositivos</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener la lista completa de dispositivos disponibles
                        </div>
                        <div class="response">
                            <h4>Respuesta exitosa (200):</h4>
                            <div class="example">
{
    "data": {
        "tableData": [...]
    }
}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/mis-dispositivos</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener los dispositivos asociados a un usuario específico
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">usuario</span>
                                    <span class="param-type">integer</span>
                                    <span class="param-required">requerido</span>
                                    <div>ID del usuario</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Ejemplo de uso:</h4>
                            <div class="example">
GET /mis-dispositivos?usuario=1
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/dispositivo</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener información detallada de un dispositivo por su patente
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">patente</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Código interno/patente del dispositivo</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Ejemplo de uso:</h4>
                            <div class="example">
GET /dispositivo?patente=ABC123
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/add-device</span>
                        <span class="method POST">POST</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Asociar un nuevo dispositivo a un usuario
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">usuario</span>
                                    <span class="param-type">integer</span>
                                    <span class="param-required">requerido</span>
                                    <div>ID del usuario (en la URL)</div>
                                </div>
                            </div>
                            <h4>Parámetros (JSON Body):</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">patente</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Código del dispositivo</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">modelo</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Modelo del dispositivo</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Ejemplo de uso:</h4>
                            <div class="example">
POST /add-device?usuario=1
{
    "patente": "ABC123",
    "modelo": "Eolo MP Express"
}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="sessions">
                <h2>📊 Sesiones</h2>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/sesiones</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener todas las sesiones disponibles desde archivo JSON
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/sesion</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener información de una sesión específica por ID
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">id_sesion</span>
                                    <span class="param-type">integer</span>
                                    <span class="param-required">requerido</span>
                                    <div>ID de la sesión</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/mis-sesiones</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener las sesiones asociadas a una patente específica
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">patente</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Patente del dispositivo</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/add-session</span>
                        <span class="method POST">POST</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Crear una nueva sesión de medición. También disponible en el endpoint principal.
                        </div>
                        <div class="params">
                            <h4>Parámetros (JSON Body):</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">filename</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Nombre del archivo de datos</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">patente</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Patente del dispositivo</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">lat</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Latitud de la sesión</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">lon</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Longitud de la sesión</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">fecha_inicial</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Fecha y hora de inicio (ISO format)</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">fecha_final</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Fecha y hora de finalización (ISO format)</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">volumen</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Volumen medido</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">flujo</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Flujo promedio</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">bateria</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Nivel de batería</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="data">
                <h2>📈 Datos</h2>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/datos</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener todas las mediciones de una sesión específica
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">id_sesion</span>
                                    <span class="param-type">integer</span>
                                    <span class="param-required">requerido</span>
                                    <div>ID de la sesión</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/datos</span>
                        <span class="method POST">POST</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Insertar múltiples mediciones en lote
                        </div>
                        <div class="params">
                            <h4>Parámetros (JSON Body):</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">id_sesion</span>
                                    <span class="param-type">integer</span>
                                    <span class="param-required">requerido</span>
                                    <div>ID de la sesión</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">mediciones</span>
                                    <span class="param-type">array</span>
                                    <span class="param-required">requerido</span>
                                    <div>Array de objetos con datos de medición</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/datos/insert</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Insertar una medición individual mediante parámetros de URL
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">patente</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Patente del dispositivo</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">id_sesion</span>
                                    <span class="param-type">integer</span>
                                    <span class="param-required">requerido</span>
                                    <div>ID de la sesión</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">timestamp</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Timestamp de la medición</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">temperatura_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor de temperatura</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">humedad_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor de humedad</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">presion_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor de presión atmosférica</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">pm2.5_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor de PM2.5</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">pm10_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor de PM10</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">bateria_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Nivel de batería</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">velocidad_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Velocidad del viento</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">direccion_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Dirección del viento</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">flujo_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor del flujo</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">volumen_valor</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Valor del volumen</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="utils">
                <h2>🔧 Utilidades</h2>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/upload</span>
                        <span class="method POST">POST</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Subir y procesar archivos Excel con datos de sensores
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">patente</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Patente del dispositivo (en la URL)</div>
                                </div>
                            </div>
                            <h4>Archivo:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">file</span>
                                    <span class="param-type">file</span>
                                    <span class="param-required">requerido</span>
                                    <div>Archivo Excel (.xls o .xlsx) con datos de mediciones</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Formato esperado del archivo Excel:</h4>
                            <div class="example">
Columnas requeridas:
- timestamp: Unix timestamp
- temperatura_valor: Temperatura (°C)
- humedad_valor: Humedad (%)
- presion_valor: Presión (hPa)
- pm2.5_valor: PM2.5 (μg/m³)
- pm10_valor: PM10 (μg/m³)
- bateria_valor: Batería (%)
- velocidad_valor: Velocidad viento (m/s)
- direccion_valor: Dirección viento (°)
- flujo_valor: Flujo (m³/h)
- volumen_valor: Volumen (m³)
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/geocode</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener coordenadas (latitud y longitud) a partir de una dirección
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">location</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Dirección o nombre del lugar</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Ejemplo de uso:</h4>
                            <div class="example">
GET /geocode?location=Santiago, Chile

Respuesta:
{
    "lat": "-33.4488897",
    "lon": "-70.6692655"
}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/geocode-reverse</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Obtener información de dirección a partir de coordenadas
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">lat</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Latitud</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">lon</span>
                                    <span class="param-type">float</span>
                                    <span class="param-required">requerido</span>
                                    <div>Longitud</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/validate-pin</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Validar un PIN generado para una patente específica
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">text</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Patente del dispositivo</div>
                                </div>
                                <div class="param">
                                    <span class="param-name">pin</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>PIN a validar</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span>/get-pin</span>
                        <span class="method GET">GET</span>
                    </div>
                    <div class="endpoint-body">
                        <div class="endpoint-description">
                            Generar un PIN para una patente específica
                        </div>
                        <div class="params">
                            <h4>Parámetros de consulta:</h4>
                            <div class="param-list">
                                <div class="param">
                                    <span class="param-name">text</span>
                                    <span class="param-type">string</span>
                                    <span class="param-required">requerido</span>
                                    <div>Patente del dispositivo</div>
                                </div>
                            </div>
                        </div>
                        <div class="response">
                            <h4>Respuesta:</h4>
                            <div class="example">
{
    "input": "ABC123",
    "pin": "1234"
}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                <p><strong>🌪️ EOLO API</strong> - Sistema de Monitoreo Ambiental</p>
                <p>Desarrollado para el seguimiento y análisis de datos ambientales en tiempo real</p>
                <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                    📧 Para soporte técnico, contactar al equipo de desarrollo
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    from flask import Response
    return Response(html_content, content_type='text/html; charset=utf-8')


# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        patente = request.args.get('patente')

        print("Patente recibida:", patente)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Leer el archivo Excel usando pandas
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
                # Verificar si ya existe un registro con ese filename y patente
                check_sql = "SELECT COUNT(*) AS count FROM sesiones WHERE filename = %s AND patente = %s"
                cursor.execute(check_sql, (file.filename, patente))
                result = cursor.fetchone()

                if result['count'] > 0:
                    return jsonify({"error": "Ya existe una sesión con este filename y patente asociada."}), 400
            
            connection.close()

            # Cargar el archivo Excel
            df = pd.read_excel(filepath)
            print("debug")

            # Asegurarse de que las columnas necesarias existen
            required_columns = ['timestamp', 'temperatura_valor', 'humedad_valor', 'presion_valor']
            for column in required_columns:
                if column not in df.columns:
                    return jsonify({"error": f"Falta la columna {column} en el archivo."}), 400

            # Obtener la primera fila y la última fila
            first_row = df.iloc[0]
            last_row = df.iloc[-1]


            # Extraer los datos de la primera fila para el inicio
            timestamp_inicial = datetime.utcfromtimestamp(first_row['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')
            
            # Extraer los datos de la última fila para el final
            timestamp_final = datetime.utcfromtimestamp(last_row['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

            volumen = str(last_row['volumen_valor'])
            flujo = str((first_row["flujo_valor"] + last_row["flujo_valor"]) / 2)
            bateria = str(last_row['bateria_valor'])
            print("bateria", bateria)

            # Crear el diccionario para las filas que solo contienen la primera y última fila
            session_data = {
                'patente': patente,
                'timestamp_inicial': timestamp_inicial,
                'timestamp_final': timestamp_final,
                'volumen': volumen,
                "flujo": flujo,
                "bateria": bateria,
            }

            
            # Convertir el DataFrame a JSON
            file_json = df.to_dict(orient='records')  # Convertir todo el DataFrame a formato de lista de diccionarios
            print(file_json)

            
            # Necesario para luego guardar los datos en tabla datos. 
            # Guardar el JSON procesado en un archivo
            with open(JSON_FILES_SESIONES_JSON + "/"+ file.filename + ".json", 'w', encoding='utf-8') as json_file:
                json.dump(file_json, json_file, ensure_ascii=False, indent=2)
            
            # Devolver el resultado solo con la primera y última fila
            return jsonify({"message": "Archivo procesado exitosamente", "data": [session_data], "mediciones": file_json}), 200
        
        except Exception as e:
            return jsonify({"error": f"Ocurrió un error al procesar el archivo: {str(e)}"}), 500

    else:
        return jsonify({"error": "Archivo no permitido. Solo se permiten archivos .xls y .xlsx"}), 400



# Endpoint para obtener coordenadas de una ubicación
@app.route('/geocode', methods=['GET', 'OPTIONS'])
def geocode_location():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    location = request.args.get('location')  # Obtener la ubicación desde los parámetros de la URL

    if not location:
        return jsonify({"error": "No location provided"}), 400

    try:

        
        # Agregar el encabezado User-Agent para evitar el bloqueo
        headers = {
            'User-Agent': 'EOLO/1.0 (dkressing@udd.cl)'  # Agrega un correo válido o información relevante
        }

        # Solicitar a la API de Nominatim
        response = requests.get(f'https://nominatim.openstreetmap.org/search', 
                                params={'q': location, 'format': 'json'},
                                headers=headers)

        # response = requests.get('https://nominatim.openstreetmap.org/search?format=json&q=Chile')
        print(response)
        data = response.json()
        if data:
            # Tomar la primera coincidencia
            location_data = data[0]
            lat = location_data['lat']
            lon = location_data['lon']
            return jsonify({"lat": lat, "lon": lon}), 200
        else:
            return jsonify({"error": "Location not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener coordenadas de una ubicación
# Endpoint para obtener coordenadas de una ubicación
@app.route('/geocode-reverse', methods=['GET', 'OPTIONS'])
def geocode_reverse_location():
    # Manejar preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200
    
    lat = request.args.get('lat')  # Obtener la ubicación desde los parámetros de la URL
    lon = request.args.get('lon')  # Obtener la ubicación desde los parámetros de la URL

    if not lat or not lon:
        error_response = jsonify({"error": "No location provided"})
        error_response.headers.add("Access-Control-Allow-Origin", "*")
        return error_response, 400

    try:

        
        # Agregar el encabezado User-Agent para evitar el bloqueo
        headers = {
            'User-Agent': 'EOLO/1.0 (dkressing@udd.cl)'  # Agrega un correo válido o información relevante
        }

        # Solicitar a la API de Nominatim
        response = requests.get(f'https://nominatim.openstreetmap.org/reverse', 
                                params={'lat': lat,"lon": lon, 'format': 'json'},
                                headers=headers)

        data = response.json()
        # data_string = json.dumps(data, ensure_ascii=False)
        print(str(data["display_name"]))
        if data:
            # Tomar la primera coincidencia
            location_data = data
            display_name = str(location_data['display_name'])

            # Decodificar cualquier secuencia Unicode en el texto
            response_data = jsonify(data)
            response_data.headers.add("Access-Control-Allow-Origin", "*")
            response_data.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
            response_data.headers.add("Access-Control-Allow-Headers", "Content-Type")
            return response_data, 200
        else:
            error_response = jsonify({"error": "Location not found"})
            error_response.headers.add("Access-Control-Allow-Origin", "*")
            return error_response, 404

    except Exception as e:
        error_response = jsonify({"error": str(e)})
        error_response.headers.add("Access-Control-Allow-Origin", "*")
        return error_response, 500



# Ruta para validar el PIN
@app.route('/validate-pin', methods=['GET'])
def validate_pin():
    # Obtener los parámetros 'text' y 'pin' de la URL
    text = request.args.get('text')
    # if text and "-" in text:
    text = text.replace("-", "")
        
    pin = request.args.get('pin')

    # Verificar que ambos parámetros existen
    if not text or not pin:
        return jsonify({"error": "Faltan parámetros 'text' o 'pin'"}), 400

    # Generamos el PIN a partir del texto (patente)
    generated_pin = generate_pin(text)

    print(generated_pin, text)
    
    # Encriptamos el PIN generado
    
    # Validar si el PIN proporcionado coincide con el PIN generado
    if str(pin) == str(generated_pin):
        return jsonify({"message": "Valid PIN"}), 200
    else:
        print(str(pin) + "-" + str(generated_pin))
        return jsonify({"message": "PIN incorrecto"}), 400
    

# Ruta para generar el PIN
@app.route('/get-pin', methods=['GET'])
def get_pin():
    # Obtener los parámetros 'text' URL
    text = request.args.get('text')
    if not text:
        return jsonify({"error": "Faltan parámetros 'text' o 'pin'"}), 400

    # Generamos el PIN a partir del texto (patente)
    # textClean =""
    textClean = text.replace("-", "")
    # if text and "-" in text:
        # textClean = text.replace("-", "")

    generated_pin = generate_pin(textClean)
    print(generated_pin)
    
    # Validar si el PIN proporcionado coincide con el PIN generado
    return jsonify({"input": text, "pin": generated_pin}), 200


@app.route('/add-session', methods=['POST', 'OPTIONS'])
def add_session():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        # Obtener datos del request JSON
        session_data = request.get_json()
        
        # Validar que todos los campos requeridos estén presentes
        required_fields = ['filename', 'patente', 'fecha_inicial', 'fecha_final', 'volumen', 'flujo', 'lat', 'lon', 'bateria']
        for field in required_fields:
            if field not in session_data:
                return jsonify({"error": f"Falta el campo requerido: {field}"}), 400
        
        # Conectar a la base de datos
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Verificar si ya existe una sesión con el mismo filename y patente
            check_sql = "SELECT COUNT(*) AS count FROM sesiones WHERE filename = %s AND patente = %s"
            cursor.execute(check_sql, (session_data['filename'], session_data['patente']))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                return jsonify({"error": "Ya existe una sesión con este filename y patente."}), 400
            
            # Insertar la nueva sesión
            insert_sql = """
                INSERT INTO sesiones (filename, patente, fecha_inicial, fecha_final, volumen, flujo, lat, lon, bateria, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(insert_sql, (
                session_data['filename'],
                session_data['patente'],
                session_data['fecha_inicial'],
                session_data['fecha_final'],
                session_data['volumen'],
                session_data['flujo'],
                session_data['lat'],
                session_data['lon'],
                session_data['bateria']
            ))
            
            # Confirmar los cambios
            connection.commit()
        
        connection.close()
        
        return jsonify({"message": "Sesión agregada exitosamente"}), 200
        
    except Exception as e:
        print(f"Error al agregar sesión: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)
