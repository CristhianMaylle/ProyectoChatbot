# backend/app/services/function_handler.py

from app.services.measures import get_latest_measure, get_measure_history
from app.services.reminders import schedule_reminder
from app.services.alerts import send_critical_alert
from app.services.dashboard import (
    get_latest_oxygen_data,
    get_oxygen_history,
    get_critical_alert_count,
)
from sqlalchemy.ext.asyncio import AsyncSession


# Mapea los nombres de funciones GPT a funciones reales
async def handle_function_call(
    name: str, args: dict, db: AsyncSession, user_id_context=None
) -> str:
    user_id = args.get("user_id") or user_id_context
    if name == "get_latest_measure":
        print(
            f"[DEBUG] handle_function_call: name={name}, user_id={user_id}, args={args}"
        )
        measurement = await get_latest_measure(user_id, db)
        if not measurement:
            return "No se encontró ninguna medición."
        return f"Última medición: {measurement.spo2}% de oxígeno, {measurement.pulse} BPM, estado: {measurement.status}."

    elif name == "get_oxygen_history":
        rango = args.get("range", "7d")
        history = await get_measure_history(user_id, rango, db)
        if not history:
            return "No hay historial disponible."
        latest = history[-1]
        return (
            f"Última entrada en historial: {latest.spo2}% SPO2 el {latest.measured_at}."
        )

    elif name == "schedule_reminder":
        frequency = args.get("frequency")
        time = args.get("time")
        result = await schedule_reminder(user_id, frequency, db)
        return result

    elif name == "send_critical_alert":
        spo2 = args.get("spo2")
        result = await send_critical_alert(user_id, spo2, db)
        return result

    elif name == "get_dashboard_summary":
        latest = await get_latest_oxygen_data(user_id, db)
        alert_count = await get_critical_alert_count(user_id, db)
        if not latest:
            return "No hay mediciones disponibles aún."
        return (
            f"Tu nivel actual de oxígeno es {latest['spo2']}% ({latest['status']}). "
            f"Última medición: {latest['measured_at']}. "
            f"Has tenido {alert_count} alertas críticas."
        )

    elif name == "get_oxygen_history_graph":
        history = await get_oxygen_history(user_id, db)
        if not history:
            return "No hay datos históricos."
        formatted = "\n".join(
            [f"{point['timestamp']}: {point['spo2']}%" for point in history[-5:]]
        )
        return f"Historial reciente de SPO2:\n{formatted}"

    elif name == "interpret_oxygen_level":
        spo2 = args.get("spo2")
        if spo2 >= 95:
            return (
                f"Tu nivel de oxígeno es {spo2}%, lo cual es NORMAL. "
                "Los niveles normales de oxígeno en sangre están entre 95% y 100%. "
                "Esto indica que tus pulmones están funcionando bien y tu sangre está "
                "transportando adecuadamente el oxígeno a tus tejidos y órganos."
            )
        elif spo2 >= 90:
            return (
                f"Tu nivel de oxígeno es {spo2}%, lo cual requiere PRECAUCIÓN. "
                "Niveles entre 90% y 94% pueden indicar una leve hipoxemia (baja oxigenación). "
                "Esto podría ser normal en algunas condiciones como altitudes elevadas, "
                "pero si estás a nivel del mar, considera consultar a un médico, "
                "especialmente si experimentas síntomas como fatiga o dificultad para respirar."
            )
        else:
            return (
                f"Tu nivel de oxígeno es {spo2}%, lo cual es CRÍTICO. "
                "Niveles por debajo de 90% indican hipoxemia significativa y requieren "
                "atención médica inmediata. Esto puede ser signo de problemas respiratorios "
                "o cardíacos graves. Si este nivel persiste, debes buscar atención médica "
                "de emergencia o llamar a servicios de emergencia."
            )

    elif name == "interpret_heart_rate":
        heart_rate = args.get("heart_rate")
        age = args.get("age", 30)  # Valor predeterminado si no se proporciona

        # Interpretación básica de la frecuencia cardíaca
        if heart_rate < 60:
            interpretation = (
                f"Tu frecuencia cardíaca es {heart_rate} BPM, lo cual es BAJA (bradicardia). "
                "Una frecuencia cardíaca baja puede ser normal en atletas o personas con buena "
                "condición física. Sin embargo, también puede indicar problemas con el sistema "
                "eléctrico del corazón, efectos de medicamentos o trastornos de la tiroides."
            )
        elif heart_rate <= 100:
            interpretation = (
                f"Tu frecuencia cardíaca es {heart_rate} BPM, lo cual está en el rango NORMAL. "
                "El rango normal de frecuencia cardíaca en reposo para adultos es de 60-100 BPM. "
                "Una frecuencia cardíaca dentro de este rango generalmente indica un buen funcionamiento "
                "del sistema cardiovascular."
            )
        else:
            interpretation = (
                f"Tu frecuencia cardíaca es {heart_rate} BPM, lo cual es ELEVADA (taquicardia). "
                "Una frecuencia cardíaca elevada puede ser normal durante el ejercicio, estrés o ansiedad. "
                "Sin embargo, en reposo, puede indicar fiebre, deshidratación, anemia, problemas cardíacos, "
                "o efectos de cafeína, alcohol o medicamentos."
            )

        # Añadir recomendaciones basadas en la edad
        if age < 18:
            interpretation += (
                "\n\nNota: Los niños y adolescentes suelen tener frecuencias cardíacas más altas que los adultos. "
                "Consulta con un pediatra para una evaluación específica para tu edad."
            )
        elif age > 60:
            interpretation += (
                "\n\nNota: En adultos mayores, es importante monitorear regularmente la frecuencia cardíaca, "
                "especialmente si tomas medicamentos que pueden afectar el ritmo cardíaco."
            )

        return interpretation

    else:
        return f"La función '{name}' no está implementada aún."
