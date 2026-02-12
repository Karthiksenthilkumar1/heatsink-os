import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QFrame, QScrollArea, QStackedLayout)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon

from api_client import HeatSinkAPIClient
from styles import get_application_styles
from config_manager import ConfigManager
from widgets.core_tile import CoreZone
from widgets.thermal_graph import ThermalGraph
from widgets.status_header import StatusHeader
from widgets.decision_panel import DecisionPanel
from widgets.settings_panel import SettingsPanel
from widgets.history_view import HistoryView
from widgets.performance_view import PerformanceView
from widgets.core_detail_view import CoreDetailView
from widgets.hover_overlay import HoverOverlay

class HeatSinkWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeatSink-OS Dashboard")
        self.resize(1200, 800)
        
        self.api_client = HeatSinkAPIClient()
        self.config_manager = ConfigManager()
        self.core_tiles = {}
        self.last_decision_id = None
        
        # Status Stabilization (Hysteresis)
        self.status_buffer = []
        self.status_buffer_size = 5 # 5 seconds of consistency
        self.current_stable_type = "safe"
        self.current_stable_msg = "INITIALIZING..."
        
        self.init_ui()
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self._apply_settings(self.config_manager.get_settings())
        
        # Listen for settings changes
        self.config_manager.settings_changed.connect(self._apply_settings)

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(30, 20, 30, 30)
        root_layout.setSpacing(20)
        
        # 1. Persistent Header & Global Status
        self.header = StatusHeader()
        self.header.navigate.connect(self._switch_view)
        root_layout.addWidget(self.header)
        
        # 2. Main Content Stack
        self.stack = QStackedLayout()
        
        # --- VIEW: Dashboard ---
        dash_widget = QWidget()
        dash_layout = QHBoxLayout(dash_widget)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        dash_layout.setSpacing(25)
        
        # Left Dashboard: Thermal Map
        left_layout = QVBoxLayout()
        map_title = QLabel("CORE THERMAL MAP")
        map_title.setObjectName("Caption")
        left_layout.addWidget(map_title)
        
        cores_scroll = QScrollArea()
        cores_scroll.setWidgetResizable(True)
        cores_scroll.setFrameShape(QFrame.NoFrame)
        cores_container = QWidget()
        cores_container.setObjectName("CentralWidget")
        self.cores_grid = QGridLayout(cores_container)
        self.cores_grid.setSpacing(15)
        cores_scroll.setWidget(cores_container)
        left_layout.addWidget(cores_scroll)
        dash_layout.addLayout(left_layout, 2)
        
        # Right Dashboard: Insights
        right_layout = QVBoxLayout()
        right_layout.setSpacing(25)
        
        agg_panel = QFrame()
        agg_panel.setObjectName("Panel")
        agg_layout = QHBoxLayout(agg_panel)
        self.avg_metric = self._create_metric("AVG TEMP", "--°")
        self.max_metric = self._create_metric("MAX TEMP", "--°")
        agg_layout.addLayout(self.avg_metric['layout'])
        agg_layout.addSpacing(20)
        agg_layout.addLayout(self.max_metric['layout'])
        right_layout.addWidget(agg_panel)
        
        self.thermal_graph = ThermalGraph()
        right_layout.addWidget(self.thermal_graph, 1)
        
        self.decision_panel = DecisionPanel()
        right_layout.addWidget(self.decision_panel)
        dash_layout.addLayout(right_layout, 1)
        
        self.stack.addWidget(dash_widget) # Index 0: dash
        
        # --- VIEW: Performance ---
        self.perf_view = PerformanceView(self.config_manager)
        self.stack.addWidget(self.perf_view) # Index 1: perf
        
        # --- VIEW: History ---
        self.history_view = HistoryView(self.config_manager)
        self.stack.addWidget(self.history_view) # Index 2: hist
        
        # --- VIEW: Settings ---
        self.settings_panel = SettingsPanel(self.config_manager)
        self.stack.addWidget(self.settings_panel) # Index 3: sett
        
        # --- VIEW: Core Detail ---
        self.detail_view = CoreDetailView()
        self.detail_view.back_requested.connect(lambda: self._switch_view("dash"))
        self.stack.addWidget(self.detail_view) # Index 4 (Dynamic)
        
        # Overlays
        self.hover_overlay = HoverOverlay(self)
        
        root_layout.addLayout(self.stack)
        self.setStyleSheet(get_application_styles())

    def _create_metric(self, label, value):
        layout = QVBoxLayout()
        l_label = QLabel(label)
        l_label.setObjectName("Caption")
        v_label = QLabel(value)
        v_label.setObjectName("MetricValue")
        layout.addWidget(l_label)
        layout.addWidget(v_label)
        return {'layout': layout, 'label': l_label, 'value': v_label}

    def _switch_view(self, view_name):
        indices = {"dash": 0, "perf": 1, "hist": 2, "sett": 3}
        idx = indices.get(view_name, 0)
        self.stack.setCurrentIndex(idx)
        if view_name == "hist":
            self.history_view.refresh_history()
        elif view_name == "perf":
            self.perf_view.refresh_stats()
        
        # Update Nav Styles in header
        btn_mapping = {"dash": self.header.dash_btn, "perf": self.header.perf_btn, 
                       "hist": self.header.hist_btn, "sett": self.header.sett_btn}
        if view_name in btn_mapping:
            btn_mapping[view_name].setChecked(True)
            self.header._update_nav_styles()

    def _apply_settings(self, settings):
        # Apply refresh rate
        self.timer.stop()
        self.timer.start(settings.get("refresh_rate", 1000))
        
        # Thresholds are applied during refresh_data logic below
        # Numeric toggle is applied to each tile during update_data

    def refresh_data(self):
        status = self.api_client.get_status()
        is_running = status is not None
        settings = self.config_manager.get_settings()
        thresholds = settings["thresholds"]
        
        max_t = 0
        avg_t = 0
        
        # Update Core Tiles
        temps = self.api_client.get_temps()
        load = self.api_client.get_load()
        
        if temps and 'cores' in temps:
            core_data = temps['cores']
            temp_list = [d.get('temperature', 0) for d in core_data.values()]
            if temp_list:
                max_t = max(temp_list)
                avg_t = sum(temp_list) / len(temp_list)
            
            self.max_metric['value'].setText(f"{int(max_t)}°")
            self.avg_metric['value'].setText(f"{int(avg_t)}°")
            
            for i, (cid, data) in enumerate(core_data.items()):
                cid_int = int(cid)
                if cid_int not in self.core_tiles:
                    tile = CoreZone(cid_int)
                    tile.hover_enter.connect(self._on_core_hover)
                    tile.hover_leave.connect(self.hover_overlay.hide)
                    tile.clicked.connect(self._show_core_detail)
                    self.core_tiles[cid_int] = tile
                    self.cores_grid.addWidget(tile, i // 4, i % 4)
                
                cload = 0.0
                if load and cid in load:
                    cload = load[cid].get('load_percent', 0.0)
                
                # Apply Dynamic Thresholds & Visibility from Settings
                cur_temp = data.get('temperature', 0.0)
                self._update_tile_with_settings(self.core_tiles[cid_int], cur_temp, cload, settings)
                
                # Update detail view if active
                if self.stack.currentIndex() == 4 and self.detail_view.core_id == cid_int:
                    self.detail_view.update_data(cur_temp, cload)
        
        self.header.update_status(max_t, is_running)
        
        # Update Graph
        if is_running:
            pkg_temp = status.get('package_temp')
            self.thermal_graph.update_data(pkg_temp)
            
        # Update Decisions & Performance Metrics
        decision = self.api_client.get_decision()
        self.decision_panel.update_decision(decision)
        self.config_manager.update_performance_metrics(avg_t, max_t)
        
        # Calculate raw status type
        raw_type = "safe"
        raw_msg = "SYSTEM IS RUNNING COOL"
        if max_t >= thresholds["hot"]:
            raw_type = "hot"
            raw_msg = "CRITICAL: HIGH TEMPERATURE"
        elif max_t >= thresholds["warm"]:
            raw_type = "warm"
            raw_msg = "WARNING: WARMING UP"
            
        # Stabilize Status (Hysteresis)
        self.status_buffer.append((raw_type, raw_msg))
        if len(self.status_buffer) > self.status_buffer_size:
            self.status_buffer.pop(0)
            
        # Check for consistency
        types_in_buffer = [b[0] for b in self.status_buffer]
        if types_in_buffer.count(raw_type) >= 3: # Require 3/5 consistency
            self.current_stable_type = raw_type
            self.current_stable_msg = raw_msg
            
        self.header.update_status(max_t, is_running, self.current_stable_type, self.current_stable_msg)
        
        # Log unique migrations to History
        if decision and decision.get('action') == "MIGRATE":
            d_id = f"{decision.get('pid')}_{decision.get('from_core')}_{decision.get('to_core')}"
            if d_id != self.last_decision_id:
                self.config_manager.add_history_entry(decision)
                self.last_decision_id = d_id
        elif decision and decision.get('action') == "NO_ACTION":
            self.last_decision_id = None

    def _on_core_hover(self, core_id, pos):
        tile = self.core_tiles.get(core_id)
        if tile:
            temp_txt = tile.temp_label.text().replace("°", "")
            temp = float(temp_txt) if temp_txt != "●" else 0.0
            load_txt = tile.load_label.text()
            # Map load text to approximate percentage for tooltip
            load_map = {"IDLE": 2, "LIGHT": 15, "ACTIVE": 45, "HEAVY": 85}
            load_val = load_map.get(load_txt, 0)
            self.hover_overlay.update_data(core_id, temp, load_val, tile.history)
            self.hover_overlay.show_at(pos)

    def _show_core_detail(self, core_id):
        self.detail_view.set_core(core_id)
        # Update it immediately
        tile = self.core_tiles.get(core_id)
        if tile:
            temp_txt = tile.temp_label.text().replace("°", "")
            temp = float(temp_txt) if temp_txt != "●" else 0.0
            # Map load text to approximate percentage
            load_map = {"IDLE": 2, "LIGHT": 15, "ACTIVE": 45, "HEAVY": 85}
            load_val = load_map.get(tile.load_label.text(), 0)
            self.detail_view.update_data(temp, load_val)
            
        self.stack.setCurrentIndex(4) # Detail View index

    def _update_tile_with_settings(self, tile, temp, load, settings):
        # Override standard update with customizable settings
        thresholds = settings["thresholds"]
        tile.temp_label.setText(f"{int(temp)}°" if settings["show_numeric"] else "●")
        
        tile.update_data(temp, load)
        
        status = "safe"
        if temp >= thresholds["hot"]:
            status = "hot"
        elif temp >= thresholds["warm"]:
            status = "warm"
        
        if tile.property("status") != status:
            tile.setProperty("status", status)
            tile.style().unpolish(tile)
            tile.style().polish(tile)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatSinkWindow()
    window.show()
    sys.exit(app.exec())
