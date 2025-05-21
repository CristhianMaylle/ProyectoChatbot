# Oxymonitor Frontend

Frontend para la aplicación Oxymonitor, un sistema de monitoreo de niveles de oxígeno en sangre con alertas, chatbot y dashboard.

## Tecnologías

- FastAPI (para el servidor frontend)
- Jinja2 (para las plantillas)
- Bootstrap 5 (para el diseño)
- Chart.js (para los gráficos)
- JavaScript (para la interactividad)

## Requisitos

- Python 3.8+
- Pip

## Instalación

1. Clonar el repositorio:
   \`\`\`
   git clone https://github.com/tu-usuario/oxymonitor.git
   cd oxymonitor/frontend
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
   Edita el archivo `.env` con la URL de tu API backend.

## Ejecución

Para iniciar el servidor en modo desarrollo:

\`\`\`
python main.py
\`\`\`

El servidor estará disponible en `http://localhost:8080`.

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación
- `templates/`: Plantillas HTML
  - `base.html`: Plantilla base con navegación y estructura común
  - `index.html`: Página de inicio
  - `login.html`: Página de inicio de sesión
  - `register.html`: Página de registro
  - `measure.html`: Página para medir oxígeno
  - `dashboard.html`: Panel de control con gráficos y chatbot
  - `chat.html`: Página dedicada al chatbot
- `static/`: Archivos estáticos
  - `css/`: Hojas de estilo
  - `js/`: Scripts de JavaScript
  - `img/`: Imágenes

## Características

- **Autenticación**: Registro e inicio de sesión de usuarios
- **Medición de Oxígeno**: Interfaz para medir niveles de oxígeno con Arduino o manualmente
- **Dashboard**: Visualización de datos con gráficos e indicadores
- **Chatbot**: Asistente virtual para consultas sobre oxígeno y pulso
- **Recordatorios**: Sistema para programar recordatorios de medición

## Conexión con el Backend

Este frontend se conecta a un backend separado a través de API REST. Asegúrate de que el backend esté en ejecución y accesible en la URL especificada en el archivo `.env`.

## Licencia

MIT
