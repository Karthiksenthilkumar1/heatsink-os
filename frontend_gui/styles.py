def get_application_styles():
    return """
    QMainWindow {
        background-color: #0B0E11;
    }
    
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    
    QWidget#CentralWidget {
        background-color: #0B0E11;
    }

    /* Glass Panels */
    QFrame#Panel {
        background-color: rgba(22, 26, 33, 0.7);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    QFrame#HighlightPanel {
        background-color: rgba(30, 35, 45, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(88, 166, 255, 0.2);
    }

    /* Typography */
    QLabel {
        color: #E6EDF3;
        font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
    }
    
    QLabel#HeroTitle {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    QLabel#HeroStatus {
        font-size: 16px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 12px;
    }
    
    QLabel#Caption {
        font-size: 12px;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    QLabel#MetricValue {
        font-size: 36px;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* Core Zone Tiles */
    QFrame#CoreZone {
        background-color: rgba(40, 45, 55, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        min-width: 120px;
        min-height: 120px;
    }
    
    QFrame#CoreZone:hover {
        background-color: rgba(50, 60, 80, 0.6);
        border: 1px solid rgba(88, 166, 255, 0.4);
    }
    
    /* Neon Status States */
    QFrame#CoreZone[status="safe"] {
        border-bottom: 3px solid #00FFC8;
    }
    
    QFrame#CoreZone[status="warm"] {
        border-bottom: 3px solid #FFD700;
    }
    
    QFrame#CoreZone[status="hot"] {
        border-bottom: 3px solid #FF3131;
        background-color: rgba(255, 49, 49, 0.1);
    }

    /* Buttons & Controls */
    QPushButton#SecondaryButton {
        background-color: rgba(255, 255, 255, 0.1);
        color: #E6EDF3;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    QPushButton#SecondaryButton:hover {
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    QPushButton#ToggleButton[checked="true"] {
        background-color: #58A6FF;
        color: #0D1117;
    }

    /* Graph Styling */
    QFrame#GraphContainer {
        padding: 10px;
    }
    /* Shared Styles for Settings & History */
    QFrame#HistoryCard {
        background-color: rgba(30, 35, 45, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 8px;
    }
    
    QFrame#HistoryCard[action="MIGRATE"] {
        border-left: 4px solid #FFD700;
    }

    QGroupBox {
        font-weight: bold;
        color: #58A6FF;
        border: 1px solid rgba(88, 166, 255, 0.2);
        border-radius: 8px;
        margin-top: 20px;
        padding-top: 15px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    /* Sliders */
    QSlider::groove:horizontal {
        border: 1px solid #1C2128;
        height: 6px;
        background: #1C2128;
        margin: 2px 0;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background: #58A6FF;
        border: 1px solid #58A6FF;
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }

    /* Navigation */
    QPushButton#NavButton {
        background-color: transparent;
        color: #8B949E;
        font-weight: 600;
        padding: 8px 16px;
        border: none;
    }
    
    QPushButton#NavButton:hover {
        color: #FFFFFF;
    }
    
    QPushButton#NavButton[active="true"] {
        color: #58A6FF;
        border-bottom: 2px solid #58A6FF;
    }

    /* Checkboxes/Toggles */
    QCheckBox {
        color: #E6EDF3;
        spacing: 10px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        background-color: #1C2128;
        border: 1px solid #30363D;
        border-radius: 4px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #238636;
        border-color: #238636;
    }
    """
