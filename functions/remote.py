from flask import Blueprint, request, jsonify
import os
import requests
import json

# Configuración de variables de entorno
API_SENSORES_ROOT = os.getenv("API_SENSORES_ROOT")

remote_bp = Blueprint('remote', __name__)

# Endpoint para obtener estado de dispositivo remoto
@remote_bp.route('/remote/status', methods=['GET'])
def get_device_status():
    """
    Obtiene el estado de un dispositivo remoto por patente
    """
    patente = request.args.get('patente')
    if not patente:
        return jsonify({"error": "Falta el parámetro 'patente'"}), 400
    
    try:
        # Simular consulta de estado del dispositivo
        # Aquí puedes integrar con tu API de sensores o base de datos
        status = {
            "patente": patente,
            "online": True,
            "battery": 85,
            "last_connection": "2024-10-14T10:30:00Z",
            "location": {
                "lat": -33.4489,
                "lng": -70.6693
            }
        }
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({"error": f"Error al obtener estado: {str(e)}"}), 500

# Endpoint para enviar comando a dispositivo remoto
@remote_bp.route('/remote/command', methods=['POST'])
def send_command():
    """
    Envía un comando a un dispositivo remoto
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400
    
    patente = data.get('patente')
    command = data.get('command')
    
    if not patente or not command:
        return jsonify({"error": "Faltan parámetros 'patente' o 'command'"}), 400
    
    try:
        # Simular envío de comando
        # Aquí integrarías con tu sistema de comunicación con dispositivos
        response_data = {
            "patente": patente,
            "command": command,
            "status": "sent",
            "timestamp": "2024-10-14T10:30:00Z",
            "command_id": f"cmd_{patente}_{command}_{hash(str(data))}"
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Error al enviar comando: {str(e)}"}), 500

