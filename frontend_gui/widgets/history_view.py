from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

class HistoryCard(QFrame):
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryCard")
        # Apply migration-specific styling if applicable
        if entry.get("action") == "MIGRATE":
            self.setProperty("action", "MIGRATE")
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        
        # Header: Timestamp and Action
        header = QHBoxLayout()
        ts = QLabel(entry.get("timestamp", ""))
        ts.setObjectName("Caption")
        action_lbl = QLabel(entry.get("action", "NO_ACTION"))
        action_lbl.setStyleSheet("font-weight: bold; color: #58A6FF;" if entry.get("action") == "MIGRATE" else "color: #8B949E;")
        header.addWidget(ts)
        header.addStretch()
        header.addWidget(action_lbl)
        layout.addLayout(header)
        
        # Summary
        summary = QLabel(entry.get("summary", ""))
        summary.setStyleSheet("font-size: 14px; color: #FFFFFF; font-weight: 500;")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        
        # Details (Process, Core mapping)
        if entry.get("action") == "MIGRATE":
            details = QHBoxLayout()
            proc_info = QLabel(f"PID: {entry.get('pid')} • {entry.get('process_name')}")
            proc_info.setObjectName("Caption")
            core_map = QLabel(f"Core {entry.get('from_core')} → {entry.get('to_core')}")
            core_map.setObjectName("Caption")
            core_map.setStyleSheet("color: #FFD700;")
            details.addWidget(proc_info)
            details.addStretch()
            details.addWidget(core_map)
            layout.addLayout(details)

class HistoryView(QFrame):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.config_manager = config_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QHBoxLayout()
        title = QLabel("DECISION & MIGRATION HISTORY")
        title.setObjectName("HeroTitle")
        header.addWidget(title)
        header.addStretch()
        
        self.count_label = QLabel("Last 15 records")
        self.count_label.setObjectName("Caption")
        header.addWidget(self.count_label)
        layout.addLayout(header)
        
        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(0, 10, 0, 0)
        self.list_layout.setSpacing(5)
        self.list_layout.addStretch()
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        self.refresh_history()

    def refresh_history(self):
        # Clear existing cards (except stretch)
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        history = self.config_manager.get_history()
        # Re-add stretch at bottom
        self.list_layout.addStretch()
        
        # Add new cards
        for entry in history:
            card = HistoryCard(entry)
            self.list_layout.insertWidget(0, card) # Add to top
