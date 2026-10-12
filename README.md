# 🛡️ DaemonGuard
> **Smart Linux Resource Optimization, Waste Scoring & Real-Time Telemetry Engine**

DaemonGuard is a lightweight, intelligent system resource management tool for Linux environments. It combines multi-factor waste scoring, risk-aware process termination, automated policy enforcement, historical telemetry database, and desktop notifications.

---

## 🚀 Key Features

* **📊 Real-Time System Telemetry:** Live collection of process-level CPU, RAM, uptime, and state metrics using psutil.
* **🧠 Smart Waste Scoring Engine:** Multi-factor logic evaluating resource usage alongside process lifecycle to identify true resource hogs without accidental system crashes.
* **🛡️ Safe Process Guardrails:** Built-in safeguards preventing accidental termination of critical system processes (PIDs 1, 2, desktop environment managers).
* **🔔 Native Desktop Alerts:** Instant system notifications using Linux notify-send when high-risk processes exceed safety thresholds.
* **📈 Historical Telemetry (SQLite):** Time-series database logging system usage over time with line chart analytics.
* **🤖 Automated Cleanup Policy:** Configurable waste score threshold to auto-terminate resource hogs with one click.
* **⚙️ Systemd Service Support:** Runs as a persistent background daemon on system startup.

---

## 🏗️ Architecture & Modules

* **collector.py** – System telemetry gathering via psutil.
* **engine.py** – Multi-factor Waste Score calculation & Risk Classification logic.
* **actions.py** – Safe process termination and Desktop Popup Alerts (notify-send).
* **database.py** – SQLite database initialization and historical telemetry logging.
* **app.py** – Interactive Streamlit web-based control panel and analytics dashboard.

---

## 🛠️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/pasindu2173/DaemonGuard.git
cd DaemonGuard
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```

---

## ⚙️ Running as a Systemd Service (Background Daemon)

To keep DaemonGuard active in the background automatically:

1. Copy the service definition:
```bash
sudo nano /etc/systemd/system/daemonguard.service
```
2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable daemonguard.service
sudo systemctl start daemonguard.service
```

---

## 📝 License
Distributed under the MIT License. Built for Linux Engineers and System Administrators.