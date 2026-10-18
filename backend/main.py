from fastapi.responses import FileResponse
from fastapi import FastAPI
import psutil

app = FastAPI(title="catch-the-flag")
readings = []

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
    readings.append(payload)
    return {"received": len(readings)}

@app.get("/metrics/readings")
def get_readings():
    return {"readings": readings[-50:]}  # Return the last 50 readings

@app.get("/")
def home():
    return FileResponse("dashboard/index.html")