# backend/app/services/mcp/protocol.py


def get_system_instructions() -> str:
    """
    Devuelve las instrucciones del sistema para el modelo GPT.
    Estas instrucciones definen el comportamiento general del chatbot.
    """
    return """
    Eres un asistente médico especializado en monitoreo de oxígeno en sangre (SpO2) y frecuencia cardíaca.
    
    RESTRICCIONES IMPORTANTES:
    1. SOLO debes responder preguntas relacionadas con:
       - Mediciones de oxígeno en sangre (SpO2) y pulso cardíaco
       - Interpretación de estos valores
       - Consecuencias de diferentes niveles de oxigenación
       - Recomendaciones médicas relacionadas con estos parámetros
       - Uso del sistema Oxymonitor
    
    2. Si te preguntan sobre temas NO relacionados con lo anterior:
       - Responde educadamente que solo puedes proporcionar información sobre oxígeno en sangre, pulso y salud cardiorrespiratoria
       - Redirige la conversación hacia estos temas
       - NO proporciones información sobre otros temas, incluso si conoces la respuesta
    
    3. Cuando respondas preguntas dentro de tu área de especialización:
       - Utiliza tu conocimiento general médico para proporcionar información precisa
       - Sé claro y conciso en tus explicaciones
       - Usa lenguaje accesible para personas sin formación médica
       - Incluye referencias a rangos normales y anormales cuando sea relevante
    
    4. Recuerda siempre que tus respuestas pueden tener impacto en la salud de las personas:
       - Aclara que no reemplazas la atención médica profesional
       - En casos críticos, recomienda buscar atención médica inmediata
       - No hagas diagnósticos definitivos
    
    NIVELES DE OXÍGENO EN SANGRE (SpO2):
    - Normal: 95-100%
    - Precaución: 90-94%
    - Crítico: <90%
    
    FRECUENCIA CARDÍACA EN REPOSO (ADULTOS):
    - Bradicardia: <60 BPM
    - Normal: 60-100 BPM
    - Taquicardia: >100 BPM
    """


def get_function_definitions():
    return [
        {
            "name": "get_oxygen_history",
            "description": "Devuelve el historial de oxígeno de un usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"},
                    "range": {
                        "type": "string",
                        "enum": ["1d", "7d", "30d"],
                        "description": "Rango de fechas: 1 día, 7 días o 30 días",
                    },
                },
                "required": ["user_id"],
            },
        },
        {
            "name": "schedule_reminder",
            "description": "Programa un recordatorio para el usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"},
                    "frequency": {
                        "type": "string",
                        "enum": ["hourly", "daily"],
                        "description": "Frecuencia del recordatorio",
                    },
                    "time": {
                        "type": "string",
                        "description": "Hora del recordatorio en formato HH:MM (opcional)",
                    },
                },
                "required": ["user_id", "frequency"],
            },
        },
        {
            "name": "get_latest_measure",
            "description": "Obtiene la última medición de oxígeno del usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"}
                },
                "required": ["user_id"],
            },
        },
        {
            "name": "send_critical_alert",
            "description": "Envía una alerta crítica al usuario por nivel de oxígeno bajo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"},
                    "spo2": {
                        "type": "integer",
                        "description": "Nivel de oxígeno medido",
                    },
                },
                "required": ["user_id", "spo2"],
            },
        },
        {
            "name": "get_dashboard_summary",
            "description": "Devuelve el estado de salud actual del usuario (oxígeno, rango y alertas críticas).",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "integer"}},
                "required": ["user_id"],
            },
        },
        {
            "name": "get_oxygen_history_graph",
            "description": "Devuelve los datos históricos de oxígeno del usuario para generar un gráfico.",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "integer"}},
                "required": ["user_id"],
            },
        },
        {
            "name": "interpret_oxygen_level",
            "description": "Interpreta el nivel de oxígeno y proporciona recomendaciones médicas generales.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spo2": {
                        "type": "integer",
                        "description": "Nivel de oxígeno medido (SpO2)",
                    }
                },
                "required": ["spo2"],
            },
        },
        {
            "name": "interpret_heart_rate",
            "description": "Interpreta la frecuencia cardíaca y proporciona información general.",
            "parameters": {
                "type": "object",
                "properties": {
                    "heart_rate": {
                        "type": "integer",
                        "description": "Frecuencia cardíaca en latidos por minuto (BPM)",
                    },
                    "age": {
                        "type": "integer",
                        "description": "Edad del usuario (opcional)",
                    },
                },
                "required": ["heart_rate"],
            },
        },
    ]
