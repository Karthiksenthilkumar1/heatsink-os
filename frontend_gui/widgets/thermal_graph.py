import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QColor

class ThermalGraph(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label = QLabel("TEMPERATURE TRENDS")
        self.label.setObjectName("Caption")
        layout.addWidget(self.label)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('transparent')
        self.plot_widget.setLabel('left', 'Temp', units='°C')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.1)
        
        # Elegant blue line with glow
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#58A6FF', width=3))
        self.data = []
        
        layout.addWidget(self.plot_widget)

    def update_data(self, temp):
        if temp is None:
            return
            
        self.data.append(temp)
        if len(self.data) > 60:
            self.data.pop(0)
            
        self.curve.setData(self.data)
        
        # Dynamic color based on current temp
        if temp >= 80:
            self.curve.setPen(pg.mkPen(color='#FF3131', width=3))
        elif temp >= 60:
            self.curve.setPen(pg.mkPen(color='#FFD700', width=3))
        else:
            self.curve.setPen(pg.mkPen(color='#00FFC8', width=3))
