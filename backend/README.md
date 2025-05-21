# Oxymonitor Backend

Backend para la aplicación Oxymonitor, un sistema de monitoreo de niveles de oxígeno en sangre con alertas, chatbot y dashboard.

## Tecnologías

- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- OpenAI GPT-4 para el chatbot
- JWT para autenticación
- Arduino con sensor MAX30102 para medición de oxígeno

## Requisitos

- Python 3.10+
- PostgreSQL
- Pip
- Arduino con sensor MAX30102 (opcional)

## Instalación

1. Clonar el repositorio:
   \`\`\`
   git clone https://github.com/tu-usuario/oxymonitor-backend.git
   cd oxymonitor-backend
   \`\`\`

2. Crear un entorno virtual:
   \`\`\`
   python -m venv venv
   source venv/bin/activate # En Windows: venv\Scripts\activate
   \`\`\`

3. Instalar dependencias:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Configurar variables de entorno:
   \`\`\`
   cp .env.example .env
   \`\`\`
   Edita el archivo `.env` con tus credenciales de base de datos, clave secreta y API key de OpenAI.

5. Crear las tablas en la base de datos:
   \`\`\`
   python scripts/create_tables.py
   \`\`\`

## Configuración del Arduino

1. Conecta el sensor MAX30102 al Arduino siguiendo el esquema de conexión:

   - VIN -> 5V o 3.3V (según tu Arduino)
   - GND -> GND
   - SCL -> A5 (o pin SCL en tu Arduino)
   - SDA -> A4 (o pin SDA en tu Arduino)

2. Carga el sketch proporcionado en la carpeta `arduino/` a tu Arduino.

3. Prueba la conexión con el script de prueba:
   \`\`\`
   python scripts/test_arduino.py
   \`\`\`
   Ajusta el puerto en el script según tu configuración.

## Ejecución

Para iniciar el servidor en modo desarrollo:

\`\`\`
uvicorn app.main:app --reload
\`\`\`

El servidor estará disponible en `http://localhost:8000`.

La documentación de la API estará disponible en `http://localhost:8000/docs`.

## Flujos de Usuario

### Usuarios Registrados

- Pueden iniciar sesión
- Ver su historial de mediciones
- Recibir alertas personalizadas
- Interactuar con el chatbot sobre sus datos históricos

### Usuarios No Registrados

- Pueden realizar mediciones sin crear una cuenta
- Interactuar con el chatbot sobre su medición actual
- Los datos se almacenan como "Usuario No Identificado"

## Endpoints Principales

- `/api/auth/login`: Iniciar sesión
- `/api/users/register`: Registrar nuevo usuario
- `/api/measures/`: Registrar medición de oxígeno
- `/api/measures/sensor`: Medir oxígeno directamente desde el sensor Arduino
- `/api/measures/anonymous`: Registrar medición para usuario no identificado
- `/api/dashboard/`: Obtener datos para el dashboard
- `/api/chat/`: Interactuar con el chatbot (usuario registrado)
- `/api/chat/anonymous`: Interactuar con el chatbot (sin registro)
- `/api/reminders/`: Gestionar recordatorios

## Licencia

MIT
\`\`\`

```python file="arduino/oxymonitor_sketch/oxymonitor_sketch.ino"
#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

MAX30105 particleSensor; // Objeto para interactuar con el sensor MAX30102

#define MAX_BRIGHTNESS 255

#if defined(_AVR_ATmega328P) || defined(AVR_ATmega168_)
  // En placas con poca memoria (como Arduino Uno), usamos 16 bits por muestra
  uint16_t irBuffer[100];  // Datos de luz infrarroja
  uint16_t redBuffer[100]; // Datos de luz roja
#else
  // En placas con más memoria, usamos 32 bits por muestra
  uint32_t irBuffer[100];
  uint32_t redBuffer[100];
#endif

int32_t bufferLength;     // Longitud del buffer de muestras
int32_t spo2;             // Valor calculado de oxigenación en sangre (SpO₂)
int8_t validSPO2;         // Indicador de validez del cálculo de SpO₂

byte readLED = 13;        // LED que parpadea con cada lectura de datos

void setup()
{
  Serial.begin(115200); // Inicializamos el puerto serial a 115200 baudios

  pinMode(readLED, OUTPUT); // LED indicador de lectura de datos

  // Inicializamos el sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST))
  {
    Serial.println(F("MAX30105 no encontrado. Revisa el cableado o la alimentación."));
    while (1); // Se detiene si el sensor no está conectado correctamente
  }

  Serial.println(F("Coloca el sensor en el dedo. Presiona una tecla para comenzar."));
  while (Serial.available() == 0); // Espera hasta que el usuario presione algo
  Serial.read(); // Limpia el buffer

  // Configuración del sensor: brillo, promedios, modo, etc.
  byte ledBrightness = 60;
  byte sampleAverage = 4;
  byte ledMode = 2; // Solo rojo + IR
  byte sampleRate = 100;
  int pulseWidth = 411;
  int adcRange = 4096;

  // Aplicamos la configuración al sensor
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
}

void loop()
{
  bufferLength = 100; // Almacenaremos 100 muestras (4 segundos a 25 muestras/seg)

  // Llenamos los primeros 100 datos
  for (byte i = 0; i &lt; bufferLength; i++)
  {
    while (!particleSensor.available()) // Esperamos nueva muestra
      particleSensor.check();

    redBuffer[i] = particleSensor.getRed(); // Capturamos datos del LED rojo
    irBuffer[i] = particleSensor.getIR();   // Capturamos datos del LED IR
    particleSensor.nextSample();           // Avanzamos al siguiente dato

    digitalWrite(readLED, !digitalRead(readLED)); // Parpadea el LED de lectura

    // Solo mostramos datos crudos para verificar que llegan correctamente
    Serial.print(F("red="));
    Serial.print(redBuffer[i], DEC);
    Serial.print(F(", ir="));
    Serial.println(irBuffer[i], DEC);
  }

  // Cálculo inicial del SpO₂ con los primeros 100 datos
  // Eliminamos la frecuencia cardíaca para evitar saturación del buffer serial
  maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, nullptr, nullptr);

  // Bucle continuo para actualizar la medición de oxígeno cada segundo
  while (1)
  {
    // Desplazamos las últimas 75 muestras al inicio del buffer
    for (byte i = 25; i &lt; 100; i++)
    {
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25] = irBuffer[i];
    }

    // Tomamos 25 nuevas muestras para actualizar el cálculo
    for (byte i = 75; i &lt; 100; i++)
    {
      while (!particleSensor.available())
        particleSensor.check();

      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample();

      digitalWrite(readLED, !digitalRead(readLED)); // Parpadea el LED de lectura

      // Enviamos sólo los datos relevantes al Plotter Serial
      Serial.print("red=");
      Serial.print(particleSensor.getRed());
      Serial.print(", ir=");
      Serial.print(particleSensor.getIR());
      Serial.print(", SPO2=");
      Serial.println(spo2);
    }

    // Recalculamos el valor de SpO₂
    maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, nullptr, nullptr);
  }
}
```
