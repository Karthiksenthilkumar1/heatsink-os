# ❄️ HeatSink-OS

[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status: Research-Beta](https://img.shields.io/badge/Status-Research--Beta-orange.svg)](#)

> **"Stopping thermal throttling before it stops you."**

HeatSink-OS is a proactive, thermal-aware workload orchestrator. Designed for high-temperature climates and budget hardware, it intelligently migrates heavy CPU tasks across cores to prevent firmware-level thermal throttling, ensuring sustained performance during intense workloads.

---

## ⚡ Key Highlights

- **Dynamic Thermal Mapping**: Real-time monitoring of per-core temperatures and system-wide thermal trends.
- **Proactive Core Migration**: Moves demanding processes *before* critical thresholds are reached, preventing the performance "death spiral" of thermal throttling.
- **Predictive Analytics**: Uses historic thermal trends to anticipate heat spikes based on current workload patterns.
- **Sleek Control Tower**: A modern, high-fidelity PySide6 dashboard for visual monitoring and manual core management.
- **API-First Design**: Backend logic exposed via FastAPI, allowing for head-less operation or custom monitoring integrations.

---

## 🏗️ Architecture

The system operates as a continuous "Observe-Decide-Act" loop:

- **Sensors**: Grabs real-time data from CPU thermal zones and system load counters.
- **Orchestrator**: The central brain that maintains the system state and manages the control loop.
- **Decision Engine**: Combines current temps, load reports, and predictions to determine if a migration is required.
- **Migrator**: Interfaces with system APIs to adjust core affinity and rebalance workloads dynamically.

---

## 🚀 Quick Start

### 1. Requirements
Ensure you have Python 3.9+ installed.

```bash
# Recommended: Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows (Adjust for your shell)
```

### 2. Installation
```bash
pip install -r requirements.txt  # Ensure dependencies are met
```

### 3. Running the System
Start the backend orchestrator:
```bash
python backend/main.py
```

Launch the visual dashboard:
```bash
python frontend_gui/main.py
```

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, psutil
- **Frontend**: PySide6 (Qt for Python), modern CSS styling
- **Analysis**: Custom thermal trend algorithms & predictive modeling

---

## 🗺️ Roadmap

- [x] Initial core-migration logic
- [x] PySide6 Dashboard integration
- [ ] Integration with hardware-specific FAN control
- [ ] Machine Learning based thermal prediction (Model v2)

---

*Developed with ❤️ for high-performance computing in tropical climates.*
