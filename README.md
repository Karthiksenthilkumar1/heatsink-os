# ❄️ HeatSink-OS

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0058DD?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![PySide6](https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=Qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **"Stopping thermal throttling before it stops you."**

HeatSink-OS is a proactive, thermal-aware workload orchestrator designed for high-performance computing in challenging thermal environments. By intelligently migrating demanding CPU tasks between cores *before* critical thresholds are reached, it prevents firmware-level thermal throttling and ensures sustained, predictable performance.

---

## ⚡ Key Highlights

- **Proactive Core Migration**: Moves heavy processes based on real-time thermal trends, not just current temperatures.
- **Intelligent Migration Modes**: Choose between `Smart`, `Thermal-First`, `Performance-First`, and `Conservative` strategies.
- **Predictive Analytics**: Extrapolates heating rates to anticipate heat spikes 10 seconds into the future.
- **High-Fidelity Control Tower**: A modern PySide6 dashboard with real-time per-core thermal mapping and trend visualization.
- **API-First Architecture**: Decoupled backend logic exposed via FastAPI, enabling custom integrations and headless operation.

---

## 🏗️ Architecture: The "Observe-Decide-Act" Loop

HeatSink-OS operates as a continuous high-frequency control loop (default 0.5s interval):

1.  **Observe**: 
    - `ThermalSensor`: Polls hardware thermal zones via WMI (Windows) or high-fidelity simulation (macOS).
    - `ProcessMonitor`: Maps per-core load and identifies heavy candidates for migration.
2.  **Analyze**:
    - `ThermalTrend`: Computes heating/cooling rates and identifies "Heating Fast" cores.
    - `Predictor`: Projects temperatures into a 10s horizon to catch spikes early.
3.  **Decide**:
    - `DecisionEngine`: Evaluates core safety scores, load distribution, and cooldown constraints.
    - `MigrationModeFilter`: Refines decisions based on user-selected performance or thermal priorities.
4.  **Act**:
    - `Migrator`: Interfaces with system APIs to adjust CPU affinity for specific PIDs.

---

## 🎮 The Control Tower (Dashboard)

The PySide6-based dashboard provides a premium monitoring experience:

- **Thermal Map**: Real-time per-core status with visual indicators for P-Cores vs E-Cores.
- **Temperature Trends**: Dynamic SVG-rendered graphs showing package temperature history.
- **Insights & Decisions**: Live log of orchestrator actions and migration reasoning.
- **System Summary**: At-a-glance health status and calculated efficiency gains.

---

## 🚀 Quick Start

### 1. Environment Setup
HeatSink-OS requires Python 3.9+.

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 2. Installation
```bash
# Install core dependencies (FastAPI, uvicorn, psutil, requests)
pip install -r backend/requirements-mac.txt  # For macOS
# pip install -r requirements.txt            # For Windows
```

### 3. Running HeatSink-OS
Start the backend orchestrator first:
```bash
python backend/main.py
```

In a separate terminal, launch the dashboard:
```bash
python frontend_gui/main.py
```

---

## 🛠️ Tech Arsenal

- **Backend Logic**: Python, `psutil` (Affinity & Load), `FastAPI` (Orchestration API).
- **Frontend GUI**: `PySide6` (Qt for Python), `pyqtgraph` (Real-time plotting).
- **Communication**: `requests` (API interaction), `uvicorn` (ASGI Server).
- **Branding**: Modern CSS skinning with a focus on high-fidelity "Control Room" aesthetics.

---

*Developed with ❤️ for resilient computing.*
