from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QPoint
import pyqtgraph as pg

class HoverOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setObjectName("HoverOverlay")
        self.setStyleSheet("""
            QFrame#HoverOverlay {
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel { color: #E6EDF3; font-size: 12px; }
        """)
        
        layout = QVBoxLayout(self)
        self.title = QLabel("Core Trend")
        self.title.setStyleSheet("font-weight: bold; color: #58A6FF;")
        layout.addWidget(self.title)
        
        # Sparkline Graph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setFixedSize(180, 80)
        self.plot_widget.setBackground(None)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.hideAxis('left')
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color="#58A6FF", width=2))
        layout.addWidget(self.plot_widget)
        
        self.info = QLabel("Loading data...")
        layout.addWidget(self.info)
        
        self.temp_history = []

    def update_data(self, core_id, temp, load_metric, history, core_type="E-Core", fatigue=0, trend_metric=None):
        self.title.setText(f"CORE {core_id} ({core_type})")
        
        load = load_metric.get("load_percent", 0.0)
        power = load_metric.get("power_watts", 0.0)
        trend_status = trend_metric.get("status", "STABLE") if trend_metric else "STABLE"
        
        info_txt = f"Temp: {int(temp)}°C | Load: {int(load)}%\n"
        info_txt += f"Power: {power:.1f}W | {trend_status}\n"
        
        if fatigue > 7:
            info_txt += "⚠️ FATIGUE: Core needs rest\n"
        elif trend_status == "HEATING_FAST":
            info_txt += "🚀 PROACTIVE: Moving threads soon"
            
        self.info.setText(info_txt)
        self.curve.setData(history)
        
    def show_at(self, pos):
        self.move(pos + QPoint(20, 0))
        self.show()
