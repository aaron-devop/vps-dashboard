# 📊 VPS Dashboard

![Python](https://img.shields.io/badge/python-3.x-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge)

**A lightweight, zero-dependency Web Dashboard for Linux Servers.**

Visualize your server's health (CPU, RAM, Disk) in real-time with a Cyberpunk-styled web interface. No Nginx, Apache, or heavy monitoring tools required. Just one Python script.

## 🚀 FEATURES

* **Real-time Monitoring:** Updates every 2 seconds via AJAX.
* **Zero Dependencies:** Runs on standard Python 3 `http.server`.
* **Visual Interface:** Beautiful, dark-mode CSS dashboard.
* **Lightweight:** Consumes negligible resources (<1% CPU).

## 📥 INSTALLATION & USAGE

### 1. Download
```bash
wget [https://raw.githubusercontent.com/aaron-devop/vps-dashboard/main/vps_dashboard.py](https://raw.githubusercontent.com/aaron-devop/vps-dashboard/main/vps_dashboard.py)
```

### 2. Run the Dashboard
```bash
# Run simply (stops when you close terminal)
sudo python3 vps_dashboard.py

# OR Run in background (keeps running)
nohup sudo python3 vps_dashboard.py &
```

### 3. Access
Open your web browser and navigate to:
`http://YOUR_SERVER_IP:8080`

_(Make sure port 8080 is allowed in your firewall!)_

## 🖼️ PREVIEW

The dashboard displays:
* **CPU Load:** Visual bar & load average.
* **RAM Usage:** Used/Total memory.
* **Disk Space:** Root partition usage.
* **System Info:** Hostname, Kernel, Uptime.

## 📜 LICENSE
MIT License
