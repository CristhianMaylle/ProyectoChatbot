# scripts/test_arduino_live.py
import sys
import os
import asyncio
import time

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.arduino_sensor import ArduinoSensor
from app.services.measures import classify_oxygen_level


async def monitor_arduino():
    """Monitorea en tiempo real los datos del sensor Arduino."""
    print("=== MONITOR EN TIEMPO REAL DE ARDUINO ===")
    print("Presiona Ctrl+C para detener.")

    # Puedes cambiar el puerto según tu configuración
    port = input("Ingresa el puerto del Arduino (ej: COM3, /dev/ttyACM0): ") or "COM3"

    sensor = ArduinoSensor(port=port)

    if not sensor.connect():
        print("No se pudo conectar al sensor. Verifica la conexión y el puerto.")
        return

    print("\nConexión establecida. Monitoreando datos en tiempo real...")
    print("SpO2\t|\tPulso\t|\tEstado\t|\tLecturas Válidas")
    print("-" * 60)

    try:
        while True:
            data = await sensor.read_sensor()

            if "error" in data:
                print(f"Error: {data['error']}")
            else:
                status = classify_oxygen_level(data["spo2"])
                print(
                    f"{data['spo2']}%\t|\t{data['pulse']} BPM\t|\t{status}\t|\t{data['valid_readings']}"
                )

            # Esperar antes de la siguiente lectura
            await asyncio.sleep(2)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    finally:
        sensor.disconnect()
        print("Sensor desconectado.")


if __name__ == "__main__":
    asyncio.run(monitor_arduino())
