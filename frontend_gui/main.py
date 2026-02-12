import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import QTimer, Qt

from api_client import HeatSinkAPIClient
from styles import get_application_styles
from widgets.core_tile import CoreTile
from widgets.thermal_graph import ThermalGraph

class HeatSinkWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeatSink-OS Desktop")
        self.resize(1000, 700)
        
        self.api_client = HeatSinkAPIClient()
        self.core_tiles = {}
        
        self.init_ui()
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1000) # Update every second

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_container = QVBoxLayout()
        self.title_label = QLabel("HeatSink-OS Dashboard")
        self.title_label.setObjectName("Title")
        self.subtitle_label = QLabel("System Thermal Orchestration • Windows")
        self.subtitle_label.setObjectName("Subtitle")
        title_container.addWidget(self.title_label)
        title_container.addWidget(self.subtitle_label)
        header_layout.addLayout(title_container)
        
        self.status_badge = QLabel("STATUS: INITIALIZING")
        self.status_badge.setStyleSheet("color: #D29922; font-weight: bold; border: 1px solid #D29922; border-radius: 4px; padding: 4px 8px;")
        header_layout.addWidget(self.status_badge, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        main_layout.addLayout(header_layout)
        
        # Content Split: Left (Cores), Right (Graph/Details)
        content_layout = QHBoxLayout()
        
        # Cores Section
        cores_scroll = QScrollArea()
        cores_scroll.setWidgetResizable(True)
        cores_scroll.setFrameShape(QFrame.NoFrame)
        cores_scroll.setStyleSheet("background: transparent;")
        
        cores_container = QWidget()
        self.cores_grid = QGridLayout(cores_container)
        self.cores_grid.setSpacing(10)
        cores_scroll.setWidget(cores_container)
        
        content_layout.addWidget(cores_scroll, 2)
        
        # Right Sidebar (Graph & Decision)
        sidebar_layout = QVBoxLayout()
        
        self.thermal_graph = ThermalGraph()
        sidebar_layout.addWidget(self.thermal_graph)
        
        self.decision_frame = QFrame()
        self.decision_frame.setObjectName("Dashboard")
        decision_vbox = QVBoxLayout(self.decision_frame)
        decision_title = QLabel("LATEST DECISION")
        decision_title.setObjectName("Subtitle")
        decision_vbox.addWidget(decision_title)
        
        self.decision_label = QLabel("No active migrations")
        self.decision_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        self.decision_label.setWordWrap(True)
        decision_vbox.addWidget(self.decision_label)
        
        sidebar_layout.addWidget(self.decision_frame)
        content_layout.addLayout(sidebar_layout, 1)
        
        main_layout.addLayout(content_layout)
        
        self.setStyleSheet(get_application_styles())

    def refresh_data(self):
        status = self.api_client.get_status()
        if not status:
            self.status_badge.setText("STATUS: BACKEND OFFLINE")
            self.status_badge.setStyleSheet("color: #F85149; font-weight: bold; border: 1px solid #F85149; border-radius: 4px; padding: 4px 8px;")
            return
            
        self.status_badge.setText(f"STATUS: {status.get('status', 'ACTIVE')}".upper())
        self.status_badge.setStyleSheet("color: #3FB950; font-weight: bold; border: 1px solid #3FB950; border-radius: 4px; padding: 4px 8px;")
        
        # Update Cores
        temps = self.api_client.get_temps()
        load = self.api_client.get_load()
        
        if temps and 'cores' in temps:
            core_data = temps['cores']
            for i, (cid, data) in enumerate(core_data.items()):
                cid_int = int(cid)
                if cid_int not in self.core_tiles:
                    tile = CoreTile(cid_int)
                    self.core_tiles[cid_int] = tile
                    row = i // 3
                    col = i % 3
                    self.cores_grid.addWidget(tile, row, col)
                
                cload = 0.0
                if load and cid in load:
                    cload = load[cid].get('load_percent', 0.0)
                
                self.core_tiles[cid_int].update_data(data.get('temperature', 0.0), cload)
        
        # Update Graph
        pkg_temp = status.get('package_temp')
        if pkg_temp:
            self.thermal_graph.update_data(pkg_temp)
            
        # Update Decision
        decision = self.api_client.get_decision()
        if decision and decision.get('action') == "MIGRATE":
            msg = f"MIGRATING PID {decision.get('pid')} to Core {decision.get('to_core')}"
            self.decision_label.setText(msg)
            self.decision_label.setStyleSheet("font-size: 16px; color: #D29922; font-weight: bold;")
        else:
            self.decision_label.setText("System balanced. No migration needed.")
            self.decision_label.setStyleSheet("font-size: 16px; color: #8B949E;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatSinkWindow()
    window.show()
    sys.exit(app.exec())
