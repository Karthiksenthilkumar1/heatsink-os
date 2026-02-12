import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

class ThermalGraph(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dashboard")
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Thermal History (CPU Package)")
        self.label.setObjectName("Subtitle")
        layout.addWidget(self.label)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#161A21')
        self.plot_widget.setLabel('left', 'Temp', units='°C')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#58A6FF', width=2))
        self.data = []
        
        layout.addWidget(self.plot_widget)

    def update_data(self, temp):
        if temp is None:
            return
            
        self.data.append(temp)
        if len(self.data) > 60: # Keep last 60 points (30s at 0.5s interval)
            self.data.pop(0)
            
        self.curve.setData(self.data)
