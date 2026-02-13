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
        
        metrics_row = QHBoxLayout()
        self.temp_metric = self._create_metric("CURRENT TEMP", "--°C")
        self.load_metric = self._create_metric("CORE LOAD", "--%")
        self.trend_metric = self._create_metric("THERMAL OUTLOOK", "STABLE")
        metrics_row.addLayout(self.temp_metric)
        metrics_row.addLayout(self.load_metric)
        metrics_row.addLayout(self.trend_metric)
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
        info_row = QHBoxLayout()
        
        v_events = QVBoxLayout()
        self.event_label = QLabel("RECENT CORE EVENTS")
        self.event_label.setObjectName("Caption")
        v_events.addWidget(self.event_label)
        self.event_list = QLabel("No recent migrations detected.")
        self.event_list.setStyleSheet("color: #8B949E; font-size: 13px;")
        self.event_list.setWordWrap(True)
        v_events.addWidget(self.event_list)
        v_events.addStretch()
        info_row.addLayout(v_events, 1)
        
        v_procs = QVBoxLayout()
        self.proc_label = QLabel("CORE PROCESSES")
        self.proc_label.setObjectName("Caption")
        v_procs.addWidget(self.proc_label)
        self.proc_list = QLabel("Scanning for heavy threads...")
        self.proc_list.setStyleSheet("color: #8B949E; font-size: 13px;")
        v_procs.addWidget(self.proc_list)
        v_procs.addStretch()
        info_row.addLayout(v_procs, 1)
        
        layout.addLayout(info_row)
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

    def set_core(self, core_id, history_data=[]):
        self.core_id = core_id
        self.title.setText(f"CORE {core_id:02d} DETAILS")
        self.history = []
        self.curve.setData([])
        
        # Filter relevant history events
        relevant = [h for h in history_data if h.get('from_core') == core_id or h.get('to_core') == core_id]
        if relevant:
            txt = ""
            for r in relevant[:5]:
                marker = "OUT" if r.get('from_core') == core_id else "IN"
                txt += f"• [{marker}] {r['process_name']} ({r['timestamp'][-8:]})\n"
            self.event_list.setText(txt)
        else:
            self.event_list.setText("No recent migration events.")

    def update_data(self, temp, load, top_processes=[], trend=None, prediction=None):
        self.temp_metric.itemAt(1).widget().setText(f"{int(temp)}°C")
        self.load_metric.itemAt(1).widget().setText(f"{int(load)}%")
        
        # Trend & Prediction Logic
        outlook = "STABLE"
        if trend:
            outlook = trend.get('status', 'STABLE')
            if prediction and prediction.get('predicted_increase', 0) > 0.5:
                # Show prediction in parenthesis
                inc = prediction['predicted_increase']
                outlook += f" (+{inc:.1f}°C est.)"
        
        self.trend_metric.itemAt(1).widget().setText(outlook)
        self.trend_metric.itemAt(1).widget().setStyleSheet(
            "color: #FF3131;" if "HEATING" in outlook or "+" in outlook else "color: #58A6FF;"
        )
        
        self.history.append(temp)
        if len(self.history) > 60: self.history.pop(0)
        self.curve.setData(self.history)
        
        if top_processes:
            p_txt = "\n".join([f"• {p['name']} (PID: {p['pid']})" for p in top_processes[:3]])
            self.proc_list.setText(p_txt)
