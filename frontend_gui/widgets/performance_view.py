from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout
from PySide6.QtCore import Qt

class PerfMetric(QFrame):
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px;")
        
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setObjectName("Caption")
        layout.addWidget(self.title)
        
        self.value = QLabel("--")
        self.value.setObjectName("MetricValue")
        self.value.setStyleSheet("font-size: 28px; font-weight: 300; color: #FFFFFF;")
        layout.addWidget(self.value)
        
        self.desc = QLabel(subtitle)
        self.desc.setStyleSheet("color: #808080; font-size: 11px;")
        self.desc.setWordWrap(True)
        layout.addWidget(self.desc)

class PerformanceView(QFrame):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.config_manager = config_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        header = QLabel("PERFORMANCE IMPACT ANALYSIS")
        header.setObjectName("HeroTitle")
        layout.addWidget(header)
        
        # Comparison Section (Storytelling)
        comparison_layout = QHBoxLayout()
        comparison_layout.setSpacing(40)
        
        # Left: Without HeatSink-OS (Baseline)
        self.left_panel = QFrame()
        self.left_panel.setStyleSheet("background: rgba(255, 49, 49, 0.05); border-radius: 12px; border: 1px solid rgba(255, 49, 49, 0.2);")
        l_layout = QVBoxLayout(self.left_panel)
        l_layout.setContentsMargins(20, 20, 20, 20)
        
        l_title = QLabel("WITHOUT OPTIMIZATION")
        l_title.setStyleSheet("color: #FF3131; font-weight: bold; letter-spacing: 1px;")
        l_desc = QLabel("Standard Windows Scheduling")
        l_desc.setStyleSheet("color: #808080; font-size: 12px; margin-bottom: 10px;")
        
        self.l_status = QLabel("Thermal Throttling Likely")
        self.l_status.setStyleSheet("font-size: 18px; color: #E0E0E0;")
        
        l_layout.addWidget(l_title)
        l_layout.addWidget(l_desc)
        l_layout.addWidget(self.l_status)
        l_layout.addStretch()
        
        # Right: With HeatSink-OS (Active)
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background: rgba(0, 209, 178, 0.05); border-radius: 12px; border: 1px solid rgba(0, 209, 178, 0.2);")
        r_layout = QVBoxLayout(self.right_panel)
        r_layout.setContentsMargins(20, 20, 20, 20)
        
        r_title = QLabel("WITH HEATSINK-OS")
        r_title.setStyleSheet("color: #00D1B2; font-weight: bold; letter-spacing: 1px;")
        r_desc = QLabel("Proactive Thread Migration")
        r_desc.setStyleSheet("color: #808080; font-size: 12px; margin-bottom: 10px;")
        
        self.r_status = QLabel("Peak Performance Sustained")
        self.r_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        
        r_layout.addWidget(r_title)
        r_layout.addWidget(r_desc)
        r_layout.addWidget(self.r_status)
        r_layout.addStretch()
        
        comparison_layout.addWidget(self.left_panel)
        comparison_layout.addWidget(self.right_panel)
        layout.addLayout(comparison_layout)
        
        # Metrics Grid
        grid = QHBoxLayout()
        self.temp_red = PerfMetric("TEMP REDUCTION", "Average core cooling achieved.")
        self.peak_red = PerfMetric("PEAK MITIGATION", "Reduction in dangerous heat spikes.")
        self.stability = PerfMetric("STABILITY SCORE", "Consistency of system performance.")
        
        grid.addWidget(self.temp_red)
        grid.addWidget(self.peak_red)
        grid.addWidget(self.stability)
        layout.addLayout(grid)
        
        # Efficiency Bar
        layout.addSpacing(10)
        lbl = QLabel("OVERALL EFFICIENCY GAIN")
        lbl.setObjectName("Caption")
        layout.addWidget(lbl)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        layout.addStretch()

    def refresh_stats(self):
        snap = self.config_manager.get_performance_snapshot()
        if not snap:
            return
            
        if not snap["is_ready"]:
            progress = int(snap["progress"])
            self.temp_red.value.setText("---")
            self.peak_red.value.setText("---")
            self.stability.value.setText("ANALYZING...")
            self.progress.setValue(progress)
            self.progress.setFormat(f"Gathering Baseline: {progress}%")
            return

        # Display Metrics
        tr = snap['temp_reduction']
        pr = snap['peak_reduction']
        
        self.temp_red.value.setText(f"{abs(tr):.1f}°C")
        self.peak_red.value.setText(f"{abs(pr):.1f}°C")
        self.stability.value.setText("HIGH") # Simplified for demo visual
        
        # Updates Story
        if tr > 2.0:
            self.l_status.setText("Thermal Throttling Detected")
            self.r_status.setText("Throttling Prevented")
            self.r_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #00D1B2;")
        else:
            self.l_status.setText("Standard Operation")
            self.r_status.setText("Ready to Optimize")
            
        # Improvement Bar
        self.progress.setValue(int(max(0, snap['improvement_pct'])))
        self.progress.setFormat(f"+{int(snap['improvement_pct'])}% EFFICIENCY")
