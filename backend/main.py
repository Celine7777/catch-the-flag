from fastapi import FastAPI
import psutil

app = FastAPI(title="catch-the-flag")

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