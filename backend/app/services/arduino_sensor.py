# backend/app/services/arduino_sensor.py

import serial
import time
import re
from typing import Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Expresiones regulares para extraer valores
SPO2_PATTERN = re.compile(r"SPO2=(\d+)")
HR_PATTERN = re.compile(r"HR=(\d+)")
HR_VALID_PATTERN = re.compile(r"HRValid=(\d+)")
SPO2_VALID_PATTERN = re.compile(r"SPO2Valid=(\d+)")


class ArduinoSensor:
    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_connected = False

    def connect(self) -> bool:
        """Conecta con el sensor Arduino."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Esperar a que Arduino se reinicie
            self.is_connected = True
            print(f"✅ Conectado al sensor en {self.port}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con el sensor: {e}")
            self.is_connected = False
            return False

    def disconnect(self) -> None:
        """Desconecta el sensor Arduino."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
            print("Sensor desconectado")

    def _read_sensor_data(self) -> Dict:
        """Lee datos del sensor en un hilo separado usando el enfoque simplificado."""
        if not self.is_connected:
            if not self.connect():
                return {"error": "Sensor no conectado"}

        try:
            # Limpiar buffer de entrada
            self.serial_conn.reset_input_buffer()

            # Leer varias líneas para obtener una medición estable
            valid_readings = []

            # Intentar leer hasta 10 líneas
            for _ in range(10):
                if self.serial_conn.in_waiting or True:  # Siempre intentar leer
                    line = self.serial_conn.readline().decode("utf-8").strip()
                    print(f"Datos desde Arduino: {line}")

                    # Extraer valores con regex
                    spo2_match = SPO2_PATTERN.search(line)
                    hr_match = HR_PATTERN.search(line)
                    hr_valid_match = HR_VALID_PATTERN.search(line)
                    spo2_valid_match = SPO2_VALID_PATTERN.search(line)

                    # Si todos los valores están presentes y son válidos
                    if spo2_match and hr_match and hr_valid_match and spo2_valid_match:

                        # Convertir a enteros
                        spo2 = int(spo2_match.group(1))
                        hr = int(hr_match.group(1))
                        hr_valid = int(hr_valid_match.group(1))
                        spo2_valid = int(spo2_valid_match.group(1))

                        # Solo considerar lecturas válidas
                        if hr_valid == 1 and spo2_valid == 1:
                            valid_readings.append({"spo2": spo2, "pulse": hr})

                # Pequeña pausa entre lecturas
                time.sleep(0.1)

            # Si tenemos al menos una lectura válida
            if valid_readings:
                # Calcular promedios
                avg_spo2 = sum(reading["spo2"] for reading in valid_readings) // len(
                    valid_readings
                )
                avg_pulse = sum(reading["pulse"] for reading in valid_readings) // len(
                    valid_readings
                )

                # Validar que el valor de SpO2 sea razonable (0-100%)
                if 0 <= avg_spo2 <= 100:
                    return {
                        "spo2": avg_spo2,
                        "pulse": avg_pulse,
                        "valid_readings": len(valid_readings),
                    }
                else:
                    return {"error": "Valor de SpO2 fuera de rango"}
            else:
                return {"error": "No se recibieron lecturas válidas del sensor"}

        except Exception as e:
            print(f"Error al leer datos del sensor: {e}")
            return {"error": str(e)}

    async def read_sensor(self) -> Dict:
        """Lee datos del sensor de forma asíncrona."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._read_sensor_data)


# Instancia global del sensor
sensor = ArduinoSensor()
