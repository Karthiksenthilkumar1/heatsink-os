from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QGroupBox, QFileDialog, QPushButton)
from PySide6.QtCore import Qt

class SettingsPanel(QFrame):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.config_manager = config_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QLabel("APPLICATION SETTINGS")
        header.setObjectName("HeroTitle")
        layout.addWidget(header)
        
        # 1. Thermal Thresholds
        threshold_group = QGroupBox("Thermal Thresholds")
        t_layout = QVBoxLayout(threshold_group)
        
        self.safe_slider = self._add_slider_setting(t_layout, "Safe Limit (°C)", 40, 80)
        self.warm_slider = self._add_slider_setting(t_layout, "Warm Limit (°C)", 60, 90)
        self.hot_slider = self._add_slider_setting(t_layout, "Hot Limit (°C)", 80, 100)
        layout.addWidget(threshold_group)
        
        # 2. Update Frequency
        refresh_group = QGroupBox("Update Frequency")
        r_layout = QVBoxLayout(refresh_group)
        self.refresh_slider = self._add_slider_setting(r_layout, "Refresh Interval (ms)", 500, 5000)
        layout.addWidget(refresh_group)
        
        # 3. Preferences
        pref_group = QGroupBox("Visual & Logging Preferences")
        p_layout = QVBoxLayout(pref_group)
        self.show_numeric_cb = QCheckBox("Show per-core numeric values")
        self.show_pred_cb = QCheckBox("Show prediction overlays")
        self.enable_log_cb = QCheckBox("Enable decision logging")
        p_layout.addWidget(self.show_numeric_cb)
        p_layout.addWidget(self.show_pred_cb)
        p_layout.addWidget(self.enable_log_cb)
        layout.addWidget(pref_group)
        
        # 4. Export Location
        export_group = QGroupBox("Logs Export Location")
        e_layout = QHBoxLayout(export_group)
        self.path_label = QLabel("C:/...")
        self.path_label.setObjectName("Caption")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("SecondaryButton")
        self.browse_btn.clicked.connect(self._select_path)
        e_layout.addWidget(self.path_label, 1)
        e_layout.addWidget(self.browse_btn)
        layout.addWidget(export_group)
        
        layout.addStretch()
        
        # Save Button
        self.save_btn = QPushButton("APPLY & SAVE SETTINGS")
        self.save_btn.setObjectName("SecondaryButton")
        self.save_btn.setStyleSheet("background-color: #238636; min-height: 40px;")
        self.save_btn.clicked.connect(self._save_settings)
        layout.addWidget(self.save_btn)

        self._load_current_values()

    def _add_slider_setting(self, parent_layout, label_text, min_val, max_val):
        row = QVBoxLayout()
        header = QHBoxLayout()
        label = QLabel(label_text)
        label.setObjectName("Caption")
        val_label = QLabel("0")
        val_label.setObjectName("Caption")
        header.addWidget(label)
        header.addStretch()
        header.addWidget(val_label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.valueChanged.connect(lambda v: val_label.setText(str(v)))
        
        row.addLayout(header)
        row.addWidget(slider)
        parent_layout.addLayout(row)
        return slider

    def _load_current_values(self):
        s = self.config_manager.get_settings()
        self.safe_slider.setValue(int(s["thresholds"]["safe"]))
        self.warm_slider.setValue(int(s["thresholds"]["warm"]))
        self.hot_slider.setValue(int(s["thresholds"]["hot"]))
        self.refresh_slider.setValue(s["refresh_rate"])
        self.show_numeric_cb.setChecked(s["show_numeric"])
        self.show_pred_cb.setChecked(s["show_predictions"])
        self.enable_log_cb.setChecked(s["enable_logging"])
        self.path_label.setText(s["export_path"])

    def _select_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if path:
            self.path_label.setText(path)

    def _save_settings(self):
        new_settings = {
            "thresholds": {
                "safe": float(self.safe_slider.value()),
                "warm": float(self.warm_slider.value()),
                "hot": float(self.hot_slider.value())
            },
            "refresh_rate": self.refresh_slider.value(),
            "show_numeric": self.show_numeric_cb.isChecked(),
            "show_predictions": self.show_pred_cb.isChecked(),
            "enable_logging": self.enable_log_cb.isChecked(),
            "export_path": self.path_label.text()
        }
        self.config_manager.save_settings(new_settings)
