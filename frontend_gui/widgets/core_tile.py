from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QPoint
from PySide6.QtGui import QColor

class CoreZone(QFrame):
    hover_enter = Signal(int, QPoint)
    hover_leave = Signal()
    clicked = Signal(int)
    
    def __init__(self, core_id, parent=None):
        super().__init__(parent)
        self.setObjectName("CoreZone")
        self.core_id = core_id
        
        # Shadow Effect for Elevation
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
        
        # Animation
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # Main Layout - Minimalist
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 1. Top Identifier (Small)
        top_row = QHBoxLayout()
        self.id_label = QLabel(f"C{core_id}")
        self.id_label.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 10px; font-weight: bold;")
        top_row.addWidget(self.id_label)
        top_row.addStretch()
        
        # Status Dot (Activity Indicator)
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("font-size: 8px; color: #303030;") 
        top_row.addWidget(self.status_dot)
        layout.addLayout(top_row)
        
        # 2. Main Visual (Temperature Number)
        self.temp_label = QLabel("--")
        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setStyleSheet("font-size: 32px; font-weight: 300; color: #FFFFFF;")
        layout.addWidget(self.temp_label)
        
        # 3. Bottom Label (Type)
        self.type_label = QLabel("P-CORE" if core_id < 4 else "E-CORE")
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.setStyleSheet("color: rgba(255,255,255,0.2); font-size: 9px; letter-spacing: 1px;")
        layout.addWidget(self.type_label)
        
        # Store state for optimizations
        self.setProperty("status", "safe")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.last_status = None # Force update on first data push

    def update_data(self, temp, load_metric, trend_metric=None, core_type=None, fatigue=0):
        # Update Temp
        self.temp_label.setText(f"{int(temp)}°")
        
        # Update Type Logic
        if core_type:
            self.type_label.setText(core_type.upper())

        # Determine Status
        load = load_metric.get("load_percent", 0.0)
        is_active = load > 5.0
        
        status = "safe"
        if temp > 90.0:
            status = "hot"
        elif temp >= 75.0 or fatigue > 5:
            status = "warm"
            
        # Visual State Updates
        if self.last_status != status:
            self.setProperty("status", status)
            self.style().unpolish(self)
            self.style().polish(self)
            self.last_status = status
            
            # Color temp label based on heat
            if status == "hot":
                self.temp_label.setStyleSheet("font-size: 32px; font-weight: 600; color: #DC3545;")
            elif status == "warm":
                self.temp_label.setStyleSheet("font-size: 32px; font-weight: 500; color: #FFC107;")
            else:
                self.temp_label.setStyleSheet("font-size: 32px; font-weight: 300; color: #FFFFFF;")

        # Active Indicator
        if is_active:
             self.status_dot.setStyleSheet("font-size: 8px; color: #00D1B2;") # Active Green
        else:
             self.status_dot.setStyleSheet("font-size: 8px; color: rgba(255,255,255,0.1);")

    def enterEvent(self, event):
        # Animate shadow bloom
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(25)
        self.anim.start()
        
        self.hover_enter.emit(self.core_id, event.globalPos())
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Animate shadow return
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(10)
        self.anim.start()
        
        self.hover_leave.emit()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.core_id)
        super().mousePressEvent(event)
