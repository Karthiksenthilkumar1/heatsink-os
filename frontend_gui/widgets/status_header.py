from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PySide6.QtCore import Qt, Signal

class StatusHeader(QFrame):
    navigate = Signal(str) # Emits view name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        top_row = QHBoxLayout()
        # Left: App Identity
        brand_layout = QVBoxLayout()
        self.title = QLabel("HeatSink-OS")
        self.title.setObjectName("HeroTitle")
        self.subtitle = QLabel("INTELLIGENT THERMAL ORCHESTRATION")
        self.subtitle.setObjectName("Caption")
        brand_layout.addWidget(self.title)
        brand_layout.addWidget(self.subtitle)
        top_row.addLayout(brand_layout)
        
        top_row.addStretch()
        
        # Center: High-Level Status
        self.status_panel = QFrame()
        self.status_panel.setObjectName("HighlightPanel")
        status_layout = QHBoxLayout(self.status_panel)
        status_layout.setContentsMargins(20, 10, 20, 10)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 20px; color: #00FFC8;")
        status_layout.addWidget(self.status_indicator)
        
        self.status_text = QLabel("SYSTEM IS RUNNING COOL")
        self.status_text.setObjectName("HeroStatus")
        status_layout.addWidget(self.status_text)
        top_row.addWidget(self.status_panel)
        
        top_row.addStretch()
        
        # Right: Quick Metric Preview
        self.mini_metric = QLabel("MAX: --°")
        self.mini_metric.setObjectName("Caption")
        self.mini_metric.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        top_row.addWidget(self.mini_metric)
        
        layout.addLayout(top_row)
        
        # Bottom Row: Navigation Tabs
        nav_layout = QHBoxLayout()
        self.nav_group = QButtonGroup(self)
        
        self.dash_btn = self._add_nav_btn(nav_layout, "DASHBOARD", "dash", active=True)
        self.perf_btn = self._add_nav_btn(nav_layout, "PERFORMANCE", "perf")
        self.hist_btn = self._add_nav_btn(nav_layout, "HISTORY", "hist")
        self.sett_btn = self._add_nav_btn(nav_layout, "SETTINGS", "sett")
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

    def _add_nav_btn(self, layout, text, name, active=False):
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setChecked(active)
        btn.setProperty("active", active)
        btn.clicked.connect(lambda: self.navigate.emit(name))
        btn.clicked.connect(self._update_nav_styles)
        layout.addWidget(btn)
        self.nav_group.addButton(btn)
        return btn

    def _update_nav_styles(self):
        for btn in self.nav_group.buttons():
            is_active = btn.isChecked()
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def update_status(self, max_temp, is_running, status_type="safe", status_msg="SYSTEM IS RUNNING COOL"):
        self.mini_metric.setText(f"MAX: {int(max_temp)}°")
        if not is_running:
            self.status_text.setText("SYSTEM OFFLINE")
            self.status_indicator.setStyleSheet("font-size: 20px; color: #8B949E;")
            return
            
        self.status_text.setText(status_msg)
        
        # Color based on settings-driven status_type
        colors = {
            "safe": "#00FFC8",
            "warm": "#FFD700",
            "hot": "#FF3131"
        }
        color = colors.get(status_type, "#00FFC8")
        self.status_indicator.setStyleSheet(f"font-size: 20px; color: {color};")
