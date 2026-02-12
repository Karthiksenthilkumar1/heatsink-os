from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QPoint

class CoreZone(QFrame):
    hover_enter = Signal(int, QPoint)
    hover_leave = Signal()
    clicked = Signal(int)
    def __init__(self, core_id, parent=None):
        super().__init__(parent)
        self.setObjectName("CoreZone")
        self.core_id = core_id
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.id_label = QLabel(f"ZONE {core_id:02d}")
        self.id_label.setObjectName("Caption")
        layout.addWidget(self.id_label)
        
        # Large visual-first value
        self.temp_label = QLabel("--°")
        self.temp_label.setObjectName("MetricValue")
        layout.addWidget(self.temp_label, alignment=Qt.AlignCenter)
        
        self.load_label = QLabel("IDLE")
        self.load_label.setObjectName("Caption")
        layout.addWidget(self.load_label, alignment=Qt.AlignCenter)

    def update_data(self, temp, load):
        self.temp_label.setText(f"{int(temp)}°")
        
        # Human-readable load
        if load < 5:
            self.load_label.setText("IDLE")
        elif load < 30:
            self.load_label.setText("LIGHT")
        elif load < 70:
            self.load_label.setText("ACTIVE")
        else:
            self.load_label.setText("HEAVY")
            
        # Per-core history for hover sparkline
        if not hasattr(self, 'history'): self.history = []
        self.history.append(temp)
        if len(self.history) > 30: self.history.pop(0)

    def enterEvent(self, event):
        self.hover_enter.emit(self.core_id, event.globalPos())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_leave.emit()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.core_id)
        super().mousePressEvent(event)
