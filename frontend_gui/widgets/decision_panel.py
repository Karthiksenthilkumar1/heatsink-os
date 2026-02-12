from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

class DecisionPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("ORCHESTRATOR DECISIONS")
        title.setObjectName("Caption")
        layout.addWidget(title)
        
        self.main_msg = QLabel("Analyzing thermal patterns...")
        self.main_msg.setStyleSheet("font-size: 18px; font-weight: 600; color: #FFFFFF;")
        self.main_msg.setWordWrap(True)
        layout.addWidget(self.main_msg)
        
        self.detail_msg = QLabel("System is balanced. No immediate action required.")
        self.detail_msg.setObjectName("Caption")
        self.detail_msg.setWordWrap(True)
        layout.addWidget(self.detail_msg)
        
        layout.addStretch()
        
        # Advice footer
        self.advice_label = QLabel("🛡️ Your system is protected by HeatSink-OS")
        self.advice_label.setStyleSheet("color: #00FFC8; font-size: 11px; font-style: italic;")
        layout.addWidget(self.advice_label)

    def update_decision(self, decision):
        if not decision or decision.get('action') == "NO_ACTION":
            self.main_msg.setText("System Balanced")
            self.detail_msg.setText("Cores are within safe thermal thresholds. No migrations scheduled.")
            self.advice_label.setText("🛡️ Your system is protected by HeatSink-OS")
        elif decision.get('action') == "MIGRATE":
            pid = decision.get('pid')
            core = decision.get('to_core')
            self.main_msg.setText(f"Optimizing Task {pid}")
            self.detail_msg.setText(f"Moving heavy workload to Core {core} to reduce thermal pressure in hot zones.")
            self.advice_label.setText("⚡ Dynamic optimization in progress...")
        else:
            self.main_msg.setText("Idle State")
            self.detail_msg.setText("Waiting for thermal data from backend...")
