import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QFrame, QScrollArea, 
                             QStackedLayout, QPushButton, QButtonGroup)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon

from api_client import HeatSinkAPIClient
from styles import get_application_styles
from config_manager import ConfigManager
from graph_data_buffer import GraphDataBuffer
from widgets.core_tile import CoreZone
from widgets.thermal_graph import ThermalGraph
from widgets.summary_zone import SummaryZone
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
        self.resize(1280, 850)
        
        self.api_client = HeatSinkAPIClient()
        self.config_manager = ConfigManager()
        self.core_tiles = {}
        self.last_decision_id = None
        
        # Graph Data Buffer (Non-intrusive synchronization layer)
        self.graph_buffer = GraphDataBuffer(buffer_size=60, valid_range=(0.0, 120.0))
        
        # Status Stabilization (Hysteresis)
        self.status_buffer = []
        self.status_buffer_size = 5 # 5 seconds of consistency
        self.current_stable_type = "safe"
        
        self.init_ui()
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self._apply_settings(self.config_manager.get_settings())
        
        # Listen for settings changes
        self.config_manager.settings_changed.connect(self._apply_settings)

        # Initialize Balancer State (One-time fetch)
        # Initialize Balancer State (One-time fetch)
        # Toggle removed from UI, so we don't need to update it here.
        self.api_client.get_migration_mode()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Main Horizontal Layout (Sidebar + Content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Sidebar Navigation
        self.sidebar = QFrame()
        self.sidebar.setObjectName("NavBar")
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)
        
        self.nav_group = QButtonGroup(self)
        self.dash_btn = self._add_nav_btn(sidebar_layout, "DASHBOARD", "dash", active=True)
        self.perf_btn = self._add_nav_btn(sidebar_layout, "PERFORMANCE", "perf")
        self.hist_btn = self._add_nav_btn(sidebar_layout, "HISTORY", "hist")
        self.sett_btn = self._add_nav_btn(sidebar_layout, "SETTINGS", "sett")
        
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar)
        
        # 2. Right Content Area (Vertical: Summary -> Stack)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(20)
        
        # Summary Zone (Top)
        self.summary = SummaryZone()
        # Toggle signal removed

        content_layout.addWidget(self.summary)
        
        # Main Content Stack
        self.stack = QStackedLayout()
        
        # --- VIEW: Dashboard ---
        dash_widget = QWidget()
        dash_layout = QHBoxLayout(dash_widget)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        dash_layout.setSpacing(25)
        
        # Left Dashboard: Core Map
        left_layout = QVBoxLayout()
        map_header = QHBoxLayout()
        map_title = QLabel("CORE THERMAL MAP")
        map_title.setObjectName("SectionHeader")
        map_header.addWidget(map_title)
        map_header.addStretch()
        left_layout.addLayout(map_header)
        
        cores_scroll = QScrollArea()
        cores_scroll.setWidgetResizable(True)
        cores_scroll.setFrameShape(QFrame.NoFrame)
        cores_container = QWidget()
        cores_container.setObjectName("CentralWidget")
        self.cores_grid = QGridLayout(cores_container)
        self.cores_grid.setSpacing(15)
        cores_scroll.setWidget(cores_container)
        left_layout.addWidget(cores_scroll)
        dash_layout.addLayout(left_layout, 6) # 60% Width
        
        # Right Dashboard: Insights & Decisions
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        
        # Thermal Graph
        self.thermal_graph = ThermalGraph()
        right_layout.addWidget(self.thermal_graph)
        
        # Decision Log
        self.decision_panel = DecisionPanel()
        right_layout.addWidget(self.decision_panel)
        
        dash_layout.addLayout(right_layout, 4) # 40% Width
        
        self.stack.addWidget(dash_widget) # Index 0
        
        # --- VIEW: Performance ---
        self.perf_view = PerformanceView(self.config_manager)
        self.stack.addWidget(self._wrap_in_scroll(self.perf_view)) # Index 1
        
        # --- VIEW: History ---
        self.history_view = HistoryView(self.config_manager)
        self.stack.addWidget(self.history_view) # Index 2
        
        # --- VIEW: Settings ---
        self.sett_view = SettingsPanel(self.config_manager)
        self.sett_view.app_lock_toggled.connect(self._on_app_lock_toggle)
        self.sett_view.refresh_apps_requested.connect(self._refresh_app_list)
        self.sett_view.migration_mode_changed.connect(self._on_migration_mode_change)
        self.stack.addWidget(self._wrap_in_scroll(self.sett_view)) # Index 3
        
        # --- VIEW: Core Detail ---
        self.detail_view = CoreDetailView()
        self.detail_view.back_requested.connect(lambda: self._switch_view("dash"))
        self.stack.addWidget(self._wrap_in_scroll(self.detail_view)) # Index 4
        
        content_layout.addLayout(self.stack)
        main_layout.addWidget(content_container)
        
        # Overlays
        self.hover_overlay = HoverOverlay(self)
        self.hover_overlay.hide()
        
        self.setStyleSheet(get_application_styles())

    def _add_nav_btn(self, layout, text, name, active=False):
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setChecked(active)
        btn.setProperty("active", active)
        btn.clicked.connect(lambda: self._switch_view(name))
        layout.addWidget(btn)
        self.nav_group.addButton(btn)
        return btn

    def _update_nav_styles(self):
        for btn in self.nav_group.buttons():
            is_active = btn.isChecked()
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _wrap_in_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(widget)
        return scroll

    def _switch_view(self, view_name):
        indices = {"dash": 0, "perf": 1, "hist": 2, "sett": 3}
        idx = indices.get(view_name, 0)
        self.stack.setCurrentIndex(idx)
        
        # Update Nav State
        btn_mapping = {"dash": self.dash_btn, "perf": self.perf_btn, 
                       "hist": self.hist_btn, "sett": self.sett_btn}
        if view_name in btn_mapping:
            btn_mapping[view_name].setChecked(True)
            self._update_nav_styles()
            
        if view_name == "hist":
            self.history_view.refresh_history()
        elif view_name == "perf":
            self.perf_view.refresh_stats()

    def _apply_settings(self, settings):
        self.timer.stop()
        self.timer.start(settings.get("refresh_rate", 1000))

    # _on_balancer_toggled removed


    def refresh_data(self):
        # 1. Get Global Status (Mode, Balancer)
        # We only read mode here, NOT balancer state to avoid overriding user toggle
        # The toggle is now the single source of truth for the frontend
        mode_data = self.api_client.get_migration_mode()
        
        status = self.api_client.get_status()
        is_running = status is not None
        settings = self.config_manager.get_settings()
        thresholds = settings["thresholds"]
        
        max_t = 0
        avg_t = 0
        
        # Update Core Tiles
        temps = self.api_client.get_temps()
        load = self.api_client.get_load()
        trend_data = self.api_client.get_trend()
        status = self.api_client.get_status()
        fatigue_data = status.get('core_fatigue', {}) if status else {}
        predictions = self.api_client.get_predictions()
        
        if temps and 'cores' in temps:
            core_data = temps['cores']
            temp_list = [d.get('temperature', 0) for d in core_data.values()]
            if temp_list:
                max_t = max(temp_list)
                avg_t = sum(temp_list) / len(temp_list)
            
            for i, (cid, data) in enumerate(core_data.items()):
                cid_int = int(cid)
                if cid_int not in self.core_tiles:
                    tile = CoreZone(cid_int)
                    tile.hover_enter.connect(self._on_core_hover)
                    tile.hover_leave.connect(self.hover_overlay.hide)
                    tile.clicked.connect(self._show_core_detail)
                    self.core_tiles[cid_int] = tile
                    self.cores_grid.addWidget(tile, i // 4, i % 4)
                
                # Fix: Handle load data structure (List vs Dict)
                cload_metric = {}
                if isinstance(load, dict):
                    cload_metric = load.get(cid, {})
                elif isinstance(load, list):
                    # Assuming list format matches core index if sorted, or we need to find by core_id
                    # Fallback: try to find item with 'core_id' == cid_int
                    for item in load:
                        if item.get('core_id') == cid_int:
                            cload_metric = item
                            break
                            
                cur_temp = data.get('temperature', 0.0)
                core_type = data.get('core_type', 'E-Core')
                ctrend = trend_data.get(cid) if isinstance(trend_data, dict) else {}
                fatigue = fatigue_data.get(cid, 0)
                
                self._update_tile_with_settings(self.core_tiles[cid_int], cur_temp, cload_metric, settings, 
                                               core_type=core_type, trend=ctrend, fatigue=fatigue)
                
                # Update detail view if active
                if self.stack.currentIndex() == 4 and self.detail_view.core_id == cid_int:
                     top_procs = cload_metric.get('top_processes', [])
                     
                     cpred = None
                     if isinstance(predictions, dict):
                         cpred = predictions.get(cid)
                     elif isinstance(predictions, list):
                         pass # Handle list if needed
                         
                     self.detail_view.update_data(cur_temp, cload_metric.get('load_percent', 0.0), 
                                                 top_procs, trend=ctrend, prediction=cpred, fatigue=fatigue)
        
        # Calculate raw status type
        raw_type = "safe"
        if max_t >= thresholds["hot"]:
            raw_type = "hot"
        elif max_t >= thresholds["warm"]:
            raw_type = "warm"
            
        # Stabilize Status
        self.status_buffer.append(raw_type)
        if len(self.status_buffer) > self.status_buffer_size:
            self.status_buffer.pop(0)
            
        if self.status_buffer.count(raw_type) >= 3:
            self.current_stable_type = raw_type
            
        # Update Summary Zone
        self.summary.update_status(max_t, is_running, self.current_stable_type)
        
        # Update Graph (with data validation layer)
        if is_running:
            pkg_temp = status.get('package_temp')
            # Pass through buffer for validation and fallback handling
            validated_temp = self.graph_buffer.observe(pkg_temp)
            self.thermal_graph.update_data(validated_temp)
            
        # Update Decisions & Performance Metrics
        decision = self.api_client.get_decision()
        self.decision_panel.update_decision(decision)
        self.config_manager.update_performance_metrics(avg_t, max_t)
        
        # Update Gain in Summary
        snap = self.config_manager.get_performance_snapshot()
        if snap and snap.get('is_ready'):
            self.summary.update_gain(snap.get('improvement_pct', 0))
            
        if self.stack.currentIndex() == 1:
            self.perf_view.refresh_stats()
            
        # Log unique migrations to History
        if decision and decision.get('action') == "MIGRATE":
            d_id = f"{decision.get('pid')}_{decision.get('from_core')}_{decision.get('to_core')}"
            if d_id != self.last_decision_id:
                self.config_manager.add_history_entry(decision)
                self.last_decision_id = d_id
        elif decision and decision.get('action') == "NO_ACTION":
            self.last_decision_id = None

        if self.stack.currentIndex() == 3:
            self._refresh_app_list()

    def _on_app_lock_toggle(self, pid):
        self.api_client.toggle_app_lock(pid)
        self._refresh_app_list()

    def _refresh_app_list(self):
        apps = self.api_client.get_applications()
        self.sett_view.update_applications(apps)
        mode_data = self.api_client.get_migration_mode()
        if mode_data:
            self.sett_view.update_migration_mode(mode_data.get("mode", "smart"))
    
    def _on_migration_mode_change(self, mode):
        self.api_client.set_migration_mode(mode)

    def _toggle_settings(self):
        self._switch_view("sett")

    def _on_core_hover(self, core_id, pos):
        tile = self.core_tiles.get(core_id)
        if tile:
            temp_txt = tile.temp_label.text().replace("°", "")
            temp = float(temp_txt) if temp_txt != "●" and temp_txt != "--" else 0.0
            
            # Additional fetch just for overlay details
            status = self.api_client.get_status()
            fatigue = status.get('core_fatigue', {}).get(str(core_id), 0) if status else 0
            trend_data = self.api_client.get_trend()
            ctrend = trend_data.get(str(core_id)) if trend_data else {}
            load_data = self.api_client.get_load()
            cload_metric = load_data.get(str(core_id), {}) if load_data else {}
            core_type = tile.type_label.text() if hasattr(tile, 'type_label') else "E-CORE"
            
            history = []
            if hasattr(self, 'config_manager'):
                history = self.config_manager.get_history().get(str(core_id), [])
            
            self.hover_overlay.update_data(core_id, temp, cload_metric, history, 
                                           core_type=core_type, fatigue=fatigue, trend_metric=ctrend)
            self.hover_overlay.show_at(pos)

    def _show_core_detail(self, core_id):
        self.detail_view.set_core(core_id, self.config_manager.get_history())
        # Optimistic update
        tile = self.core_tiles.get(core_id)
        if tile:
             pass # Will update on next tick
        self.stack.setCurrentIndex(4)

    def _update_tile_with_settings(self, tile, temp, load_metric, settings, core_type=None, trend=None, fatigue=0):
        # Override standard update with customizable settings
        tile.temp_label.setText(f"{int(temp)}°" if settings["show_numeric"] else "●")
        tile.update_data(temp, load_metric, trend_metric=trend, core_type=core_type, fatigue=fatigue)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatSinkWindow()
    window.show()
    sys.exit(app.exec())
