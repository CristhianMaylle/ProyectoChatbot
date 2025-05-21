from fastapi import FastAPI, Request, Depends, HTTPException, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

app = FastAPI(title="Oxymonitor Frontend")

# Configurar archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Middleware para verificar autenticación
async def get_current_user(request: Request):
    token = request.cookies.get("auth_token")
    user_id = request.cookies.get("user_id")

    if not token or not user_id:
        return None

    # Aquí podrías verificar el token con el backend
    return {"id": user_id, "token": token}


# Rutas
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Optional[dict] = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request, user: Optional[dict] = Depends(get_current_user)
):
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/auth/login", json={"email": email, "password": password}
            )
            data = response.json()

            if "error" in data:
                return RedirectResponse(
                    url="/login?error=Invalid credentials", status_code=303
                )

            # Crear respuesta con cookies
            redirect = RedirectResponse(url="/dashboard", status_code=303)
            redirect.set_cookie(key="auth_token", value=data["token"])
            redirect.set_cookie(key="user_id", value=str(data["id"]))
            redirect.set_cookie(key="user_name", value=data["name"])

            return redirect
        except Exception as e:
            return RedirectResponse(url=f"/login?error={str(e)}", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request, user: Optional[dict] = Depends(get_current_user)
):
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: Optional[str] = Form(None),
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/users/register",
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "phone": phone or "",
                },
            )
            data = response.json()

            if "error" in data:
                return RedirectResponse(
                    url=f"/register?error={data['error']}", status_code=303
                )

            # Crear respuesta con cookies
            redirect = RedirectResponse(url="/dashboard", status_code=303)
            redirect.set_cookie(key="auth_token", value=data["token"])
            redirect.set_cookie(key="user_id", value=str(data["id"]))
            redirect.set_cookie(key="user_name", value=data["name"])

            return redirect
        except Exception as e:
            return RedirectResponse(url=f"/register?error={str(e)}", status_code=303)


@app.get("/measure", response_class=HTMLResponse)
async def measure_page(
    request: Request, user: Optional[dict] = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "measure.html", {"request": request, "user": user}
    )


@app.post("/api/measures")
async def save_measurement(
    request: Request, user: Optional[dict] = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    # Obtener datos del cuerpo de la solicitud
    data = await request.json()

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {user['token']}"}
            response = await client.post(
                f"{API_URL}/measures/", json=data, headers=headers
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: Optional[dict] = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user}
    )


@app.get("/api/dashboard")
async def get_dashboard_data(user: Optional[dict] = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {user['token']}"}
            response = await client.get(
                f"{API_URL}/dashboard/?user_id={user['id']}", headers=headers
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/measures/history/{period}")
async def get_measures_history(
    period: str, user: Optional[dict] = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {user['token']}"}
            response = await client.get(
                f"{API_URL}/dashboard/?user_id={user['id']}&days={period}",
                headers=headers,
            )
            data = response.json()
            # Extrae solo historial
            return data.get("history", [])
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reminders")
async def get_reminders(user: Optional[dict] = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {user['token']}"}
            response = await client.get(
                f"{API_URL}/reminders/?user_id={user['id']}", headers=headers
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reminders")
async def create_reminder(
    request: Request, user: Optional[dict] = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    data = await request.json()
    data["user_id"] = int(user["id"])

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {user['token']}"}
            response = await client.post(
                f"{API_URL}/reminders/", json=data, headers=headers
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reminders/{reminder_id}")
async def cancel_reminder(
    reminder_id: int, user: Optional[dict] = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {user['token']}"}
            response = await client.delete(
                f"{API_URL}/reminders/{reminder_id}?user_id={user['id']}",
                headers=headers,
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})


@app.post("/api/chat")
async def send_chat_message(
    request: Request, user: Optional[dict] = Depends(get_current_user)
):
    data = await request.json()
    message = data.get("message")

    if not message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    async with httpx.AsyncClient() as client:
        try:
            if user:
                response = await client.post(
                    f"{API_URL}/chat/",
                    json={"user_id": int(user["id"]), "message": message},
                )
            else:
                response = await client.post(
                    f"{API_URL}/chat/anonymous", json={"message": message}
                )
            print("Status code:", response.status_code)
            print("Response text:", response.text)
            # Si la respuesta no es 2xx, intenta extraer el error
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = (
                        error_data.get("detail")
                        or error_data.get("error")
                        or str(error_data)
                    )
                except Exception:
                    error_msg = response.text
                raise HTTPException(status_code=response.status_code, detail=error_msg)

            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/initiate")
async def initiate_chat(user: Optional[dict] = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        try:
            if user:
                # Usuario autenticado
                response = await client.get(f"{API_URL}/chat/initiate/{user['id']}")
            else:
                # Usuario anónimo
                response = await client.get(f"{API_URL}/chat/initiate-anonymous")

            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="auth_token")
    response.delete_cookie(key="user_id")
    response.delete_cookie(key="user_name")
    return response


@app.get("/api/arduino/connec")
async def connec_arduino():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/measures/sensor/raw")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/arduino/connect")
async def connect_arduino():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/measures/sensor/check")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/arduino/measure")
async def measure_arduino(user: Optional[dict] = Depends(get_current_user)):
    user_id = user["id"] if user else None
    print(user_id)
    async with httpx.AsyncClient() as client:
        try:
            if user_id:
                response = await client.post(
                    f"{API_URL}/measures/sensor?user_id={user_id}", timeout=30
                )
            else:
                response = await client.post(f"{API_URL}/measures/sensor", timeout=30)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
