# scripts/test_arduino.py

import sys
import os
import asyncio
import serial

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.arduino_sensor import ArduinoSensor


async def test_sensor_simple():
    """Prueba simple usando directamente la biblioteca serial."""
    try:
        print("Conectando al Arduino usando método simple...")
        arduino = serial.Serial("COM3", 115200)  # Ajusta el puerto según tu sistema

        print("Leyendo datos directamente...")
        for i in range(10):
            line = arduino.readline().decode().strip()
            print(f"Datos desde Arduino: {line}")

        arduino.close()
        print("Conexión cerrada")
    except Exception as e:
        print(f"Error: {e}")


async def test_sensor_class():
    """Prueba usando la clase ArduinoSensor."""
    # Ajusta el puerto según tu sistema
    sensor = ArduinoSensor(port="COM3")

    print("Conectando al sensor Arduino...")
    if not sensor.connect():
        print("No se pudo conectar al sensor. Verifica la conexión y el puerto.")
        return

    print("Leyendo datos del sensor...")
    try:
        for _ in range(3):  # Intentar leer 3 veces
            data = await sensor.read_sensor()
            if "error" in data:
                print(f"Error: {data['error']}")
            else:
                print(f"Datos procesados:")
                print(f"  SpO2: {data['spo2']}%")
                print(f"  Pulso: {data['pulse']} BPM")
                print(f"  Lecturas válidas: {data['valid_readings']}")
            await asyncio.sleep(1)
    finally:
        sensor.disconnect()
        print("Sensor desconectado")


if __name__ == "__main__":
    # Puedes elegir qué prueba ejecutar
    # asyncio.run(test_sensor_simple())  # Prueba simple
    asyncio.run(test_sensor_class())  # Prueba con la clase
