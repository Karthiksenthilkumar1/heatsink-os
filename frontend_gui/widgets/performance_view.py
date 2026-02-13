from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class PerfMetric(QFrame):
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(30, 35, 45, 0.4); border-radius: 12px; padding: 20px;")
        
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setObjectName("Caption")
        layout.addWidget(self.title)
        
        self.value = QLabel("--")
        self.value.setStyleSheet("font-size: 32px; font-weight: bold; color: #58A6FF;")
        layout.addWidget(self.value)
        
        self.desc = QLabel(subtitle)
        self.desc.setStyleSheet("color: #8B949E; font-size: 12px;")
        self.desc.setWordWrap(True)
        layout.addWidget(self.desc)

class PerformanceView(QFrame):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.config_manager = config_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        header = QLabel("PERFORMANCE IMPACT ANALYSIS")
        header.setObjectName("HeroTitle")
        layout.addWidget(header)
        
        # Metrics Grid
        grid = QHBoxLayout()
        self.temp_red = PerfMetric("TEMP REDUCTION", "Average core temperature decrease compared to baseline.")
        self.peak_red = PerfMetric("PEAK MITIGATION", "Reduction in maximum observed core temperature.")
        self.stability = PerfMetric("THERMAL STABILITY", "Consistency of thermal output (reduced oscillation).")
        
        grid.addWidget(self.temp_red)
        grid.addWidget(self.peak_red)
        grid.addWidget(self.stability)
        layout.addLayout(grid)
        
        # Improvement Bar
        layout.addSpacing(20)
        lbl = QLabel("ESTIMATED PERFORMANCE EFFICIENCY")
        lbl.setObjectName("Caption")
        layout.addWidget(lbl)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #30363D;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #0D1117;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #238636;
                width: 20px;
            }
        """)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        self.explainer = QLabel("Baseline metrics are collected during the first 60 seconds of each session. Comparison shows the delta achieved by HeatSink-OS optimization.")
        self.explainer.setStyleSheet("color: #8B949E; font-style: italic; margin-top: 20px;")
        self.explainer.setWordWrap(True)
        layout.addWidget(self.explainer)
        
        layout.addStretch()

    def refresh_stats(self):
        snap = self.config_manager.get_performance_snapshot()
        if not snap or snap.get('baseline_avg', 0) == 0:
            return
            
        self.temp_red.value.setText(f"-{snap['temp_reduction']:.1f}°C")
        self.peak_red.value.setText(f"-{snap['peak_reduction']:.1f}°C")
        self.progress.setValue(int(snap['improvement_pct']))
        
        stability = "HIGH" if snap['temp_reduction'] > 2 else "MODERATE"
        self.stability.value.setText(stability)
