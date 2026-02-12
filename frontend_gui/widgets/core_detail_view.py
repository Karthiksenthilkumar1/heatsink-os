from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
import pyqtgraph as pg

class CoreDetailView(QFrame):
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QHBoxLayout()
        self.title = QLabel("CORE 00 DETAILS")
        self.title.setObjectName("HeroTitle")
        header.addWidget(self.title)
        header.addStretch()
        
        back_btn = QPushButton("BACK TO DASHBOARD")
        back_btn.setObjectName("SecondaryButton")
        back_btn.clicked.connect(lambda: self.back_requested.emit())
        header.addWidget(back_btn)
        layout.addLayout(header)
        
        # Main Metrics Row
        metrics_row = QHBoxLayout()
        self.temp_metric = self._create_metric("CURRENT TEMP", "--°C")
        self.load_metric = self._create_metric("CORE LOAD", "--%")
        metrics_row.addLayout(self.temp_metric)
        metrics_row.addLayout(self.load_metric)
        layout.addLayout(metrics_row)
        
        # Large Graph
        graph_label = QLabel("60-SECOND THERMAL HISTORY")
        graph_label.setObjectName("Caption")
        layout.addWidget(graph_label)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.1)
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color="#58A6FF", width=3))
        layout.addWidget(self.plot_widget, 1)
        
        # Placeholder for events/processes
        self.event_label = QLabel("RECENT EVENTS")
        self.event_label.setObjectName("Caption")
        layout.addWidget(self.event_label)
        
        self.event_list = QLabel("No recent migrations or heavy process shifts detected for this core.")
        self.event_list.setWordWrap(True)
        self.event_list.setStyleSheet("color: #8B949E; font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.event_list)
        
        layout.addStretch()
        
        self.core_id = None
        self.history = []

    def _create_metric(self, label, val):
        l = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("Caption")
        v = QLabel(val)
        v.setObjectName("MetricValue")
        l.addWidget(lbl)
        l.addWidget(v)
        return l

    def set_core(self, core_id):
        self.core_id = core_id
        self.title.setText(f"CORE {core_id:02d} DETAILS")
        self.history = []
        self.curve.setData([])

    def update_data(self, temp, load):
        self.temp_metric.itemAt(1).widget().setText(f"{int(temp)}°C")
        self.load_metric.itemAt(1).widget().setText(f"{int(load)}%")
        
        self.history.append(temp)
        if len(self.history) > 60: self.history.pop(0)
        self.curve.setData(self.history)
