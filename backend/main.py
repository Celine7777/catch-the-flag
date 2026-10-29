from datetime import datetime, timezone
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import FastAPI
import psutil
import sqlite3

app = FastAPI(title="catch-the-flag")
readings = []

DB_PATH = Path(__file__).parent / "metrics.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_percent REAL,
            memory_percent REAL,
            battery_percent REAL,
            battery_plugged INTEGER,
            battery_seconds_left INTEGER
        )
    """)
    conn.commit()
    conn.close()
init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_percent = memory_info.percent
    battery_percent = psutil.sensors_battery().percent if psutil.sensors_battery() else None
    battery_plugged = psutil.sensors_battery().power_plugged if psutil.sensors_battery() else None
    battery_seconds_left = psutil.sensors_battery().secsleft if psutil.sensors_battery() else None
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "battery_percent": battery_percent,
        "battery_plugged": battery_plugged,
        "battery_seconds_left": battery_seconds_left
    }

@app.post("/metrics/ingest")
def ingest(payload: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO readings (timestamp, cpu_percent, memory_percent, battery_percent, battery_plugged, battery_seconds_left) VALUES (?, ?, ?, ?, ?, ?)",
                 (payload.get("timestamp"), payload.get("cpu_percent"), payload.get("memory_percent"), payload.get("battery_percent"), payload.get("battery_plugged"), payload.get("battery_seconds_left")))
    
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    conn.close()

    return {"received": count}

@app.get("/metrics/readings")
def get_readings():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, timestamp, cpu_percent, memory_percent, battery_percent, battery_plugged, battery_seconds_left FROM readings ORDER BY timestamp DESC").fetchall()
    conn.close()
    readings = [
        {"id": row[0], "cpu_percent": row[2], "memory_percent": row[3], "battery_percent": row[4], "battery_plugged": row[5], "battery_seconds_left": row[6], "timestamp": row[1]} for row in reversed(rows)
    ]
    return {"readings": readings}

@app.get("/")
def home():
    return FileResponse("dashboard/index.html")