import http.server
import socketserver
import json
import os
import platform
import shutil
import sys
import time
from datetime import datetime

# --- CONFIGURATION ---
PORT = 8080  # Ezen a porton lesz elérhető (pl. http://IP:8080)
REFRESH_RATE = 2  # Másodperc

# --- HTML TEMPLATE (Cyberpunk Style) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPS DASHBOARD | Darkcore System</title>
    <style>
        :root { --bg: #050505; --card: #111; --text: #00ff41; --accent: #d300c5; }
        body { background: var(--bg); color: var(--text); font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        .header { border-bottom: 2px solid var(--text); padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: var(--card); border: 1px solid #333; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 255, 65, 0.1); }
        .card h2 { margin-top: 0; border-bottom: 1px solid #333; padding-bottom: 10px; color: #fff; font-size: 1.2rem; }
        .stat-value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
        .bar-container { background: #222; height: 20px; width: 100%; border-radius: 10px; overflow: hidden; margin-top: 10px; border: 1px solid #444; }
        .bar { height: 100%; background: var(--text); width: 0%; transition: width 0.5s; }
        .bar.danger { background: #ff003c; }
        .log-panel { height: 200px; overflow-y: auto; font-size: 0.8rem; background: #000; border: 1px solid #333; padding: 10px; color: #aaa; }
        .blink { animation: blinker 1.5s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>SYSTEM_MONITOR <span class="blink">_LIVE</span></h1>
        <div id="clock">--:--:--</div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>CPU LOAD</h2>
            <div class="stat-value" id="cpu-val">0%</div>
            <div class="bar-container"><div class="bar" id="cpu-bar"></div></div>
            <p id="cpu-detail">Cores: -</p>
        </div>

        <div class="card">
            <h2>MEMORY USAGE</h2>
            <div class="stat-value" id="ram-val">0%</div>
            <div class="bar-container"><div class="bar" id="ram-bar"></div></div>
            <p id="ram-detail">Free: - MB</p>
        </div>

        <div class="card">
            <h2>DISK STORAGE</h2>
            <div class="stat-value" id="disk-val">0%</div>
            <div class="bar-container"><div class="bar" id="disk-bar" style="background: var(--accent);"></div></div>
            <p id="disk-detail">Free: - GB</p>
        </div>

        <div class="card">
            <h2>SYSTEM INFO</h2>
            <p><strong>Host:</strong> <span id="sys-host">-</span></p>
            <p><strong>OS:</strong> <span id="sys-os">-</span></p>
            <p><strong>Uptime:</strong> <span id="sys-uptime">-</span></p>
        </div>
    </div>

    <script>
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    // CPU
                    document.getElementById('cpu-val').innerText = data.cpu_load + '%';
                    document.getElementById('cpu-bar').style.width = data.cpu_load + '%';
                    if(data.cpu_load > 80) document.getElementById('cpu-bar').classList.add('danger');
                    else document.getElementById('cpu-bar').classList.remove('danger');
                    document.getElementById('cpu-detail').innerText = `Load Avg: ${data.load_avg}`;

                    // RAM
                    document.getElementById('ram-val').innerText = data.ram_percent + '%';
                    document.getElementById('ram-bar').style.width = data.ram_percent + '%';
                    document.getElementById('ram-detail').innerText = `Used: ${data.ram_used} / ${data.ram_total} MB`;

                    // DISK
                    document.getElementById('disk-val').innerText = data.disk_percent + '%';
                    document.getElementById('disk-bar').style.width = data.disk_percent + '%';
                    document.getElementById('disk-detail').innerText = `Free: ${data.disk_free} GB`;

                    // SYS
                    document.getElementById('sys-host').innerText = data.hostname;
                    document.getElementById('sys-os').innerText = data.os;
                    document.getElementById('sys-uptime').innerText = data.uptime;
                    
                    // Clock
                    const now = new Date();
                    document.getElementById('clock').innerText = now.toLocaleTimeString();
                });
        }
        setInterval(updateStats, 2000);
        updateStats();
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---

class SystemMonitor:
    def get_cpu_load(self):
        try:
            load1, _, _ = os.getloadavg()
            # Normalize load for visualization (rough estimate)
            core_count = os.cpu_count() or 1
            percentage = min(int((load1 / core_count) * 100), 100)
            return percentage, load1
        except:
            return 0, 0

    def get_ram_usage(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                mem = {}
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        mem[parts[0].strip()] = int(parts[1].strip().split()[0])
            total = mem.get('MemTotal', 1) // 1024
            available = mem.get('MemAvailable', 0) // 1024
            used = total - available
            percent = int((used / total) * 100)
            return percent, used, total
        except:
            return 0, 0, 0

    def get_disk_usage(self):
        total, used, free = shutil.disk_usage("/")
        percent = int((used / total) * 100)
        return percent, free // (2**30)

    def get_uptime(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        except:
            return "Unknown"

monitor = SystemMonitor()

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            cpu_p, cpu_l = monitor.get_cpu_load()
            ram_p, ram_u, ram_t = monitor.get_ram_usage()
            disk_p, disk_f = monitor.get_disk_usage()
            
            data = {
                "cpu_load": cpu_p,
                "load_avg": cpu_l,
                "ram_percent": ram_p,
                "ram_used": ram_u,
                "ram_total": ram_t,
                "disk_percent": disk_p,
                "disk_free": disk_f,
                "hostname": platform.node(),
                "os": f"{platform.system()} {platform.release()}",
                "uptime": monitor.get_uptime()
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        return # Silence console logs

# --- MAIN ---
if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            print(f"==========================================")
            print(f" 🔥 VPS DASHBOARD ONLINE")
            print(f" 👉 Open your browser: http://YOUR_SERVER_IP:{PORT}")
            print(f"==========================================")
            print(f"Press CTRL+C to stop.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error: {e}")
      
