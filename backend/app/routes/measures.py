from fastapi import APIRouter, Depends, HTTPException
from app.schemas.measure import MeasurementCreate, MeasurementOut, AnonymousMeasurement
from app.services.measures import record_measure, get_latest_measure
from app.services.arduino_sensor import sensor, ArduinoSensor
from app.services.users import get_or_create_anonymous_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=str)
async def record(data: MeasurementCreate, db: AsyncSession = Depends(get_db)):
    return await record_measure(data.user_id, data.pulse, data.spo2, db)


@router.post("/sensor", response_model=MeasurementOut)
async def measure_from_sensor(user_id: int = None, db: AsyncSession = Depends(get_db)):
    """Endpoint para medir oxígeno directamente desde el sensor Arduino."""
    try:
        # Leer datos del sensor
        sensor_data = await sensor.read_sensor()

        if "error" in sensor_data:
            raise HTTPException(status_code=500, detail=sensor_data["error"])

        # Si no se proporciona user_id, crear un usuario anónimo
        if user_id is None:
            user = await get_or_create_anonymous_user(db)
            user_id = user.id

        # Registrar la medición
        await record_measure(
            user_id=user_id, pulse=sensor_data["pulse"], spo2=sensor_data["spo2"], db=db
        )

        await db.commit()
        print(user_id)
        # Obtener la medición recién registrada
        measurement = await get_latest_measure(user_id, db)
        if measurement is None:
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener la medición recién registrada.",
            )
        return measurement
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensor/raw", response_model=dict)
async def get_raw_sensor_data():
    """Endpoint para obtener datos crudos del sensor sin guardarlos."""
    try:
        # Leer datos del sensor
        sensor_data = await sensor.read_sensor()

        if "error" in sensor_data:
            raise HTTPException(status_code=500, detail=sensor_data["error"])

        return sensor_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anonymous", response_model=MeasurementOut)
async def anonymous_measure(
    data: AnonymousMeasurement, db: AsyncSession = Depends(get_db)
):
    """Endpoint para registrar mediciones de usuarios no identificados."""
    # Crear un usuario anónimo
    anon_user = await get_or_create_anonymous_user(db)

    # Registrar la medición
    status = await record_measure(anon_user.id, data.pulse, data.spo2, db)

    # Obtener la medición recién registrada
    measurement = await get_latest_measure(anon_user.id, db)
    if measurement is None:
        raise HTTPException(
            status_code=500, detail="No se pudo obtener la medición recién registrada."
        )
    return measurement


@router.get("/sensor/check", response_model=dict)
async def check_arduino_connection():
    """
    Verifica la conexión con el sensor Arduino.
    """
    try:
        connected = sensor.connect()
        if connected:
            return {"status": "ok", "message": "Conexión exitosa con el Arduino"}
        else:
            return {"status": "error", "message": "No se pudo conectar con el Arduino"}
    except Exception as e:
        return {"status": "error", "message": f"Error al conectar con el Arduino: {e}"}


@router.get("/test/latest-measure/{user_id}", response_model=MeasurementOut)
async def test_latest_measure(user_id: int, db: AsyncSession = Depends(get_db)):
    measurement = await get_latest_measure(user_id, db)
    if measurement is None:
        raise HTTPException(
            status_code=404, detail="No se encontró medición para este usuario."
        )
    return measurement
