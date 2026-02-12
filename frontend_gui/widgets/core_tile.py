from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class CoreTile(QFrame):
    def __init__(self, core_id, parent=None):
        super().__init__(parent)
        self.setObjectName("CoreTile")
        self.core_id = core_id
        
        layout = QVBoxLayout(self)
        
        self.id_label = QLabel(f"CORE {core_id}")
        self.id_label.setObjectName("Subtitle")
        layout.addWidget(self.id_label)
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setObjectName("CoreTemp")
        layout.addWidget(self.temp_label, alignment=Qt.AlignCenter)
        
        load_layout = QHBoxLayout()
        self.load_label = QLabel("Load: --%")
        self.load_label.setObjectName("Subtitle")
        load_layout.addWidget(self.load_label)
        layout.addLayout(load_layout)

    def update_data(self, temp, load):
        self.temp_label.setText(f"{temp:.1f}°C")
        self.load_label.setText(f"Load: {load:.1f}%")
        
        # Dynamic styling based on temperature
        if temp >= 80:
            self.setProperty("status", "hot")
        elif temp >= 60:
            self.setProperty("status", "warm")
        else:
            self.setProperty("status", "cold")
            
        self.style().unpolish(self)
        self.style().polish(self)
