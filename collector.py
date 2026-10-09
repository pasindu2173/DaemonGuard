import psutil
import pandas as pd

def get_system_telemetry():
    """
    Collects live process telemetry data from Linux OS.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            info = proc.info
            ram_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0.0
            processes.append({
                'pid': info['pid'],
                'name': info['name'],
                'ram_mb': round(ram_mb, 2),
                'cpu_percent': round(info['cpu_percent'] or 0.0, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return pd.DataFrame(processes)