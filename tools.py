import psutil
import time

def monitor_resources(interval=1):
    try:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=interval)

            # Get Memory usage
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent

            print(f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%")
    except KeyboardInterrupt:
        print("Resource monitoring stopped.")

if __name__ == "__main__":
    monitor_resources()
