from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer

class SummaryZone(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setFixedHeight(120)

        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(40)

        # 1. System Identity (Left)
        brand_layout = QVBoxLayout()
        self.title_lbl = QLabel("HeatSink-OS")
        self.title_lbl.setObjectName("HeroTitle")
        self.subtitle_lbl = QLabel("ACTIVE OPTIMIZATION")
        self.subtitle_lbl.setStyleSheet("color: #00D1B2; font-weight: bold; letter-spacing: 1.5px;")
        brand_layout.addWidget(self.title_lbl)
        brand_layout.addWidget(self.subtitle_lbl)
        layout.addLayout(brand_layout)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color: rgba(255,255,255,0.1);")
        layout.addWidget(line)

        # 2. Status Indicator (Center-Left)
        status_layout = QHBoxLayout()
        
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("font-size: 32px; color: #00D1B2;") # Default Safe
        
        self.status_text_layout = QVBoxLayout()
        self.status_main = QLabel("SYSTEM SAFE")
        self.status_main.setStyleSheet("font-size: 24px; font-weight: 300; color: #FFFFFF;")
        self.status_sub = QLabel("Thermals Stabilized")
        self.status_sub.setObjectName("Caption")
        
        self.status_text_layout.addWidget(self.status_main)
        self.status_text_layout.addWidget(self.status_sub)
        
        status_layout.addWidget(self.status_icon)
        status_layout.addSpacing(15)
        status_layout.addLayout(self.status_text_layout)
        
        layout.addLayout(status_layout)
        # Spacer
        layout.addStretch()

        # 4. Performance Gain (Right)
        perf_layout = QVBoxLayout()
        self.perf_val = QLabel("+18%")
        self.perf_val.setObjectName("MetricValue")
        self.perf_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # Removing manual stylesheet to allow styled "MetricValue" to take precedence
        
        self.perf_lbl = QLabel("EFFICIENCY GAIN")
        self.perf_lbl.setObjectName("Caption")
        self.perf_lbl.setAlignment(Qt.AlignRight)
        
        perf_layout.addWidget(self.perf_val)
        perf_layout.addWidget(self.perf_lbl)
        layout.addLayout(perf_layout)

    def update_status(self, max_temp, is_running, status_type="safe"):
        """Updates the visual state based on system health."""
        if not is_running:
            self.status_main.setText("OFFLINE")
            self.status_sub.setText("Backend Disconnected")
            self.status_icon.setStyleSheet("font-size: 32px; color: #505050;")
            return

        self.status_icon.setStyleSheet(f"font-size: 32px; color: {self._get_color(status_type)};")
        
        if status_type == "safe":
            self.status_main.setText("SYSTEM SAFE")
            self.status_sub.setText("Thermals Stabilized")
        elif status_type == "warm":
            self.status_main.setText("ELEVATED")
            self.status_sub.setText("Active Cooling Required")
        elif status_type == "hot":
            self.status_main.setText("CRITICAL")
            self.status_sub.setText("Throttling Imminent")

    def update_gain(self, gain_pct):
        """Updates the efficiency gain counter."""
        self.perf_val.setText(f"+{int(gain_pct)}%")
    
    def _get_color(self, status_type):
        """Helper method to get color based on status type."""
        colors = {
            "safe": "#00D1B2",
            "warm": "#FFD700",
            "hot": "#FF3131"
        }
        return colors.get(status_type, "#00D1B2")
