import requests
import time
import random
import math
from datetime import datetime

class EoloSimulator:
    def __init__(self):
        self.base_url = "https://api-sensores.cmasccp.cl/insertarMedicion"
        self.ids_sensores = "427,427,428,428,428,428,428,429,429,429,430,430,430,431,432,433,433,433,433,433"
        self.ids_variables = "5,17,3,6,7,8,9,3,6,13,48,49,50,3,4,15,45,46,11,12"
        
        # Variables de tendencia para simular datos más realistas
        self.wind_direction_trend = random.randint(0, 360)
        self.temperature_base = 20.0
        self.humidity_base = 60.0
        self.pressure_base = 101.3
        self.lat_base = -33.4489  # Santiago
        self.lng_base = -70.6693
        self.battery_level = 100.0
        self.volume_accumulated = 0.0
        
    def generate_realistic_values(self):
        """Genera valores realistas con tendencias coherentes"""
        
        # Hora actual para simular variaciones diurnas
        current_hour = datetime.now().hour
        
        # Velocidad del viento (0-15 m/s, más viento durante el día)
        wind_speed = max(0, random.gauss(3 + (current_hour / 24) * 2, 1.5))
        wind_speed = round(min(wind_speed, 15), 2)
        
        # Dirección del viento (con tendencia pero con variación)
        self.wind_direction_trend += random.randint(-15, 15)
        self.wind_direction_trend = self.wind_direction_trend % 360
        wind_direction = round(self.wind_direction_trend, 1)
        
        # Temperatura (variación diurna + ruido)
        temp_variation = 5 * math.sin((current_hour - 6) * math.pi / 12)
        temperature = round(self.temperature_base + temp_variation + random.gauss(0, 1), 1)
        
        # Humedad (inversamente relacionada con temperatura)
        humidity = round(max(20, min(90, self.humidity_base - temp_variation * 2 + random.gauss(0, 3))), 1)
        
        # Material particulado (PM 1.0, 2.5, 10) - correlacionados
        pm1_base = random.gauss(8, 3)
        pm1 = round(max(0, pm1_base), 1)
        pm25 = round(max(pm1, pm1_base * 1.5 + random.gauss(0, 2)), 1)
        pm10 = round(max(pm25, pm25 * 1.8 + random.gauss(0, 3)), 1)
        
        # Presión atmosférica (variación lenta)
        self.pressure_base += random.gauss(0, 0.1)
        pressure = round(max(99, min(103, self.pressure_base)), 2)
        
        # Flujo y volumen (relacionados)
        flow_configured = round(random.gauss(2.5, 0.3), 2)
        flow_observed = round(flow_configured + random.gauss(0, 0.1), 2)
        
        # Volumen acumulado (se incrementa con el tiempo)
        self.volume_accumulated += flow_observed / 60  # L/min a m³/min
        volume = round(self.volume_accumulated / 1000, 3)  # Convertir a m³
        
        # Batería (se degrada lentamente)
        self.battery_level -= random.uniform(0.01, 0.05)
        battery = round(max(0, self.battery_level), 1)
        
        # Señal telefónica (0-5, entero)
        signal_strength = random.randint(0, 5)
        
        # GPS data
        speed_kmh = round(random.gauss(0, 1), 1)  # Dispositivo mayormente estático
        satellites = random.randint(4, 12)
        
        # Pequeña variación en coordenadas (deriva del GPS)
        lat = round(self.lat_base + random.gauss(0, 0.0001), 6)
        lng = round(self.lng_base + random.gauss(0, 0.0001), 6)
        
        return [
            wind_speed,          # Velocidad del viento m/s (427)
            wind_direction,      # Dirección del Viento Grados (427)
            temperature,         # Temperatura °C (428)
            humidity,            # Humedad % (428)
            pm1,                 # PM 1.0 µg/m³ (428)
            pm25,                # PM 2.5 µg/m³ (428)
            pm10,                # PM 10 µg/m³ (428)
            temperature,         # Temperatura °C (429) - mismo sensor
            humidity,            # Humedad % (429) - mismo sensor
            pressure,            # Presión atmosférica kPa (429)
            flow_configured,     # Flujo configurado L/min (430)
            volume,              # Volumen capturado m³ (430)
            flow_observed,       # Flujo observado L/min (430)
            temperature,         # Temperatura °C (431)
            battery,             # Voltaje V (432)
            signal_strength,     # Intensidad señal telefónica (433)
            speed_kmh,           # Velocidad km/h (433)
            satellites,          # Satélites (433)
            lat,                 # Latitud (433)
            lng                  # Longitud (433)
        ]
    
    def send_measurement(self):
        """Envía una medición a la API"""
        try:
            values = self.generate_realistic_values()
            valores_str = ",".join(map(str, values))
            
            params = {
                'idsSensores': self.ids_sensores,
                'idsVariables': self.ids_variables,
                'valores': valores_str
            }
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Enviando medición...")
            print(f"Valores: {valores_str}")
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Medición enviada exitosamente")
                try:
                    result = response.json()
                    print(f"Respuesta: {result}")
                except:
                    print(f"Respuesta: {response.text}")
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print("-" * 80)
    
    def run(self, interval_seconds=60):
        """Ejecuta el simulador continuamente"""
        print("🌪️  SIMULADOR EOLO MP EXPRESS INICIADO")
        print(f"📡 URL: {self.base_url}")
        print(f"⏱️  Intervalo: {interval_seconds} segundos")
        print(f"🚀 Iniciando simulación...\n")
        
        measurement_count = 0
        
        try:
            while True:
                measurement_count += 1
                print(f"📊 MEDICIÓN #{measurement_count}")
                self.send_measurement()
                
                print(f"⏳ Esperando {interval_seconds} segundos hasta la próxima medición...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Simulación detenida por el usuario")
            print(f"📈 Total de mediciones enviadas: {measurement_count}")
        except Exception as e:
            print(f"\n❌ Error crítico: {e}")

def main():
    """Función principal"""
    simulator = EoloSimulator()
    
    # Ejecutar simulación cada 60 segundos (1 minuto)
    simulator.run(interval_seconds=60)

if __name__ == "__main__":
    main()