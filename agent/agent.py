import time
import psutil
import requests

while True:
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_percent = memory_info.percent
    battery = psutil.sensors_battery()


    payload = {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "battery_percent": battery.percent if battery else None,
    }

    try:
        response = requests.post("http://localhost:8000/metrics/ingest", json=payload)
        if response.status_code == 200:
            print(f"Successfully sent metrics: {payload}")
        else:
            print(f"Failed to send metrics. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending metrics: {e}")

    time.sleep(5)  # Wait for 5 seconds before sending the next reading