# La documentacion se escuentra en su respectiva carpeta
# 📄 Esquema SQL del Proyecto de OXIBOT

Este script crea todas las tablas necesarias para el sistema, incorporando los últimos cambios y mejoras estructurales. Incluye control de usuarios, mediciones, alertas, configuraciones, recordatorios, logs de chatbot y exportaciones administrativas.

---

```sql
-- 1. Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    phone TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de mediciones (oxígeno y pulso)
CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    spo2 INTEGER NOT NULL,
    pulse INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Normal', 'Precaución', 'Crítico')),
    measured_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de alertas generadas automáticamente
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    measurement_id INTEGER REFERENCES measurements(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('correo', 'sms', 'interna')),
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ
);

-- 4. Preferencias de notificación por usuario
CREATE TABLE notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    email_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    spo2_threshold INTEGER DEFAULT 90,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Recordatorios programados por el usuario
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    frequency TEXT NOT NULL CHECK (frequency IN ('hourly', 'daily')),
    next_run TIMESTAMPTZ NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Registro de conversaciones entre usuario y chatbot
CREATE TABLE chat_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    message TEXT NOT NULL,
    context_tag TEXT,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Registro de exportaciones realizadas por administradores
CREATE TABLE admin_exports (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    export_type TEXT NOT NULL CHECK (export_type IN ('mediciones', 'alertas', 'usuarios', 'todo')),
    file_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
