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
            battery_percent REAL
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
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent
    }

@app.post("/metrics/ingest")
def ingest(payload: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO readings (cpu_percent, memory_percent, battery_percent) VALUES (?, ?, ?)",
                 (payload.get("cpu_percent"), payload.get("memory_percent"), payload.get("battery_percent")))
    
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    conn.close()

    return {"received": count}

@app.get("/metrics/readings")
def get_readings():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT timestamp, cpu_percent, memory_percent, battery_percent FROM readings ORDER BY timestamp DESC").fetchall()
    conn.close()
    readings = [
        {"cpu_percent": row[1], "memory_percent": row[2], "battery_percent": row[3], "timestamp": row[0]} for row in reversed(rows)
    ]
    return {"readings": readings}

@app.get("/")
def home():
    return FileResponse("dashboard/index.html")