
import time
import psutil
import requests
import json

from requests.help import info


prev_io = psutil.net_io_counters()
prev_time = time.time()
prev_disk = psutil.disk_io_counters()


while True:
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_percent = memory_info.percent
    battery = psutil.sensors_battery()
    disk = psutil.disk_usage('C:/')
    current_io = psutil.net_io_counters()
    current_time = time.time()
    time_delta = current_time - prev_time
    net_up_kbps = (current_io.bytes_sent - prev_io.bytes_sent) / time_delta / 1024
    net_down_kbps = (current_io.bytes_recv - prev_io.bytes_recv) / time_delta / 1024
    prev_io = current_io
    prev_time = current_time
    cur_disk = psutil.disk_io_counters()
    disk_read_kbps = (cur_disk.read_bytes - prev_disk.read_bytes) / time_delta / 1024
    disk_write_kbps = (cur_disk.write_bytes - prev_disk.write_bytes) / time_delta / 1024
    prev_disk = cur_disk
    process = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        infor = proc.info
        if infor['name'] :
            process.append({'name': infor['name'], 'pid': infor['pid'], 'cpu_percent': infor['cpu_percent'], 'memory_percent': infor['memory_percent']})

    process.sort(key=lambda x: x['cpu_percent'], reverse=True)
    top_processes = json.dumps(process[:5])  # Get top 5 processes by CPU usage

    payload = {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "disk_percent": disk.percent,
        "battery_percent": battery.percent if battery else None,
        "net_up_kbps": net_up_kbps,
        "net_down_kbps": net_down_kbps,
        "disk_read_kbps": disk_read_kbps,
        "disk_write_kbps": disk_write_kbps,
        "top_processes": top_processes,
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