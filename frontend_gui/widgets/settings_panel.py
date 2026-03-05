from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QGroupBox, QFileDialog, QPushButton, QScrollArea, QWidget, QLineEdit)
from PySide6.QtCore import Qt, Signal

class AppEntry(QFrame):
    toggle_clicked = Signal(int) # pid
    
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.pid = app_data["pid"]
        self.app_name = app_data["name"]
        self.status = app_data.get("status", "Running")
        self.setObjectName("AppEntry")
        self.setStyleSheet("""
            QFrame#AppEntry {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 5px;
            }
            QFrame#AppEntry:hover {
                border-color: #58A6FF;
            }
        """)
        
        layout = QHBoxLayout(self)
        
        # Icon/Status
        self.lock_btn = QPushButton("🔒" if app_data["is_locked"] else "🔓")
        self.lock_btn.setFixedSize(32, 32)
        
        if self.status == "Restricted":
            self.lock_btn.setDisabled(True)
            self.lock_btn.setText("🛡️")
            self.lock_btn.setStyleSheet("background-color: #21262D; border: 1px solid #30363D; border-radius: 4px; font-size: 14px; opacity: 0.5;")
        else:
            self.lock_btn.setCursor(Qt.PointingHandCursor)
            self.lock_btn.clicked.connect(lambda: self.toggle_clicked.emit(self.pid))
            if app_data["is_locked"]:
                self.lock_btn.setStyleSheet("background-color: #382324; border: 1px solid #F85149; border-radius: 4px; font-size: 16px;")
            else:
                self.lock_btn.setStyleSheet("background-color: #21262D; border: 1px solid #30363D; border-radius: 4px; font-size: 16px;")
            
        name_layout = QVBoxLayout()
        name_label = QLabel(self.app_name)
        name_label.setStyleSheet("font-weight: bold; color: #E6EDF3;")
        
        info_txt = f"PID: {self.pid}"
        if self.status == "Running":
            info_txt += f" | CPU: {app_data['cpu']:.1f}%"
        
        pid_label = QLabel(info_txt)
        pid_label.setStyleSheet("color: #8B949E; font-size: 10px;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(pid_label)
        
        layout.addWidget(self.lock_btn)
        layout.addLayout(name_layout)
        layout.addStretch()
        
        status_txt = "LOCKED" if app_data["is_locked"] else self.status.upper()
        if self.status == "Restricted":
            status_txt = "SYSTEM"
            
        status_label = QLabel(status_txt)
        color = "#F85149" if app_data["is_locked"] else ("#8B949E" if self.status == "Restricted" else "#3FB950")
        status_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
        layout.addWidget(status_label)

class SettingsPanel(QFrame):
    app_lock_toggled = Signal(int)
    refresh_apps_requested = Signal()
    migration_mode_changed = Signal(str)  # Emits mode_id when changed

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.config_manager = config_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Main Header
        header_layout = QHBoxLayout()
        header_text = QLabel("APPLICATION SETTINGS")
        header_text.setObjectName("HeroTitle")
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Main Scroll Area for Settings content
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.NoFrame)
        main_scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(20)
        
        # 1. Thermal Thresholds
        threshold_group = QGroupBox("Thermal Thresholds")
        t_layout = QVBoxLayout(threshold_group)
        self.safe_slider = self._add_slider_setting(t_layout, "Safe Limit (°C)", 40, 80)
        self.warm_slider = self._add_slider_setting(t_layout, "Warm Limit (°C)", 60, 90)
        self.hot_slider = self._add_slider_setting(t_layout, "Hot Limit (°C)", 80, 100)
        self.scroll_layout.addWidget(threshold_group)
        
        # 2. Update Frequency
        refresh_group = QGroupBox("Update Frequency")
        r_layout = QVBoxLayout(refresh_group)
        self.refresh_slider = self._add_slider_setting(r_layout, "Refresh Interval (ms)", 500, 5000)
        self.scroll_layout.addWidget(refresh_group)

        # 3. Migration Mode Selector
        mode_group = QGroupBox("Migration Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        mode_desc = QLabel("Select how aggressively the system manages thermal migrations:")
        mode_desc.setStyleSheet("color: #8B949E; font-size: 11px; margin-bottom: 10px;")
        mode_desc.setWordWrap(True)
        mode_layout.addWidget(mode_desc)
        
        from PySide6.QtWidgets import QRadioButton, QButtonGroup
        self.mode_button_group = QButtonGroup(self)
        
        modes = [
            ("smart", "🧠 Smart (Default)", "Balanced approach using existing logic"),
            ("thermal_first", "❄️ Thermal-First", "Prioritizes temperature reduction"),
            ("performance_first", "⚡ Performance-First", "Minimizes migrations for better performance"),
            ("conservative", "🔒 Conservative", "Only migrates on critical conditions")
        ]
        
        self.mode_buttons = {}
        for mode_id, mode_label, mode_desc_text in modes:
            radio = QRadioButton(mode_label)
            radio.setStyleSheet("font-size: 12px; color: #E6EDF3; padding: 5px;")
            radio.setProperty("mode_id", mode_id)
            
            desc_label = QLabel(mode_desc_text)
            desc_label.setStyleSheet("color: #8B949E; font-size: 10px; margin-left: 25px; margin-bottom: 8px;")
            
            self.mode_button_group.addButton(radio)
            self.mode_buttons[mode_id] = radio
            mode_layout.addWidget(radio)
            mode_layout.addWidget(desc_label)
        
        # Default to Smart mode
        self.mode_buttons["smart"].setChecked(True)
        self.mode_button_group.buttonClicked.connect(self._on_mode_changed)
        self.scroll_layout.addWidget(mode_group)

        # 4. Migration Control (Application Lock)
        lock_group = QGroupBox("Migration Control (App Locking)")
        l_layout = QVBoxLayout(lock_group)
        
        l_header = QHBoxLayout()
        l_desc = QLabel("Locked applications are protected from thermal migration.")
        l_desc.setStyleSheet("color: #8B949E; font-size: 11px;")
        l_header.addWidget(l_desc)
        l_header.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh List")
        self.refresh_btn.setFixedSize(100, 24)
        self.refresh_btn.setStyleSheet("font-size: 10px; background-color: #21262D; border: 1px solid #30363D; border-radius: 4px;")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(lambda: self.refresh_apps_requested.emit())
        l_header.addWidget(self.refresh_btn)
        l_layout.addLayout(l_header)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search applications...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 4px;
                color: #C9D1D9;
                padding: 5px 10px;
                font-size: 12px;
                margin-top: 5px;
            }
            QLineEdit:focus {
                border-color: #58A6FF;
            }
        """)
        self.search_bar.textChanged.connect(self._on_search_changed)
        l_layout.addWidget(self.search_bar)

        # List of apps (Mini-scroll area inside settings)
        self.app_list_container = QWidget()
        self.app_list_layout = QVBoxLayout(self.app_list_container)
        self.app_list_layout.setContentsMargins(0, 5, 0, 5)
        self.app_list_layout.setSpacing(5)
        
        l_layout.addWidget(self.app_list_container)
        self.scroll_layout.addWidget(lock_group)
        
        # 4. Preferences
        pref_group = QGroupBox("Visual & Preferences")
        p_layout = QVBoxLayout(pref_group)
        self.show_numeric_cb = QCheckBox("Show per-core numeric values")
        self.show_pred_cb = QCheckBox("Show prediction overlays")
        self.enable_log_cb = QCheckBox("Enable decision logging")
        p_layout.addWidget(self.show_numeric_cb)
        p_layout.addWidget(self.show_pred_cb)
        p_layout.addWidget(self.enable_log_cb)
        self.scroll_layout.addWidget(pref_group)
        
        # 5. Export Location
        export_group = QGroupBox("Logs Export Location")
        e_layout = QHBoxLayout(export_group)
        self.path_label = QLabel("C:/...")
        self.path_label.setObjectName("Caption")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("SecondaryButton")
        self.browse_btn.clicked.connect(self._select_path)
        e_layout.addWidget(self.path_label, 1)
        e_layout.addWidget(self.browse_btn)
        self.scroll_layout.addWidget(export_group)
        
        self.scroll_layout.addStretch()
        main_scroll.setWidget(scroll_content)
        layout.addWidget(main_scroll)
        
        # Save Button
        self.save_btn = QPushButton("APPLY & SAVE SETTINGS")
        self.save_btn.setObjectName("SecondaryButton")
        self.save_btn.setStyleSheet("background-color: #238636; min-height: 40px;")
        self.save_btn.clicked.connect(self._save_settings)
        layout.addWidget(self.save_btn)

        self.app_widgets = {} # pid -> widget
        self.full_app_list = [] # Cache for filtering
        self._load_current_values()

    def update_applications(self, app_list):
        self.full_app_list = app_list
        self._refresh_visible_apps()

    def _on_search_changed(self, text):
        self._refresh_visible_apps()

    def _refresh_visible_apps(self):
        search_text = self.search_bar.text().lower()
        filtered_apps = [app for app in self.full_app_list if search_text in app["name"].lower()]

        # Clear removed ones
        visible_pids = [app["pid"] for app in filtered_apps]
        for pid in list(self.app_widgets.keys()):
            if pid not in visible_pids:
                widget = self.app_widgets.pop(pid)
                self.app_list_layout.removeWidget(widget)
                widget.deleteLater()
        
        # Add or update
        for i, app in enumerate(filtered_apps):
            if app["pid"] not in self.app_widgets:
                widget = AppEntry(app)
                widget.toggle_clicked.connect(lambda pid: self.app_lock_toggled.emit(pid))
                self.app_widgets[app["pid"]] = widget
                self.app_list_layout.insertWidget(i, widget)
            else:
                widget = self.app_widgets[app["pid"]]
                # Update if lock status or status changed
                is_locked_ui = widget.lock_btn.text() == "🔒"
                if (is_locked_ui != app["is_locked"]) or (widget.status != app.get("status", "Running")):
                    new_widget = AppEntry(app)
                    new_widget.toggle_clicked.connect(lambda pid: self.app_lock_toggled.emit(pid))
                    self.app_list_layout.replaceWidget(widget, new_widget)
                    self.app_widgets[app["pid"]] = new_widget
                    widget.deleteLater()

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
    
    def _on_mode_changed(self, button):
        """Handle migration mode change."""
        mode_id = button.property("mode_id")
        self.migration_mode_changed.emit(mode_id)
    
    def update_migration_mode(self, mode):
        """Update the UI to reflect the current migration mode."""
        if mode in self.mode_buttons:
            self.mode_buttons[mode].setChecked(True)
