def get_application_styles():
    return """
    QMainWindow {
        background-color: #0F1216;
    }
    
    QFrame#Dashboard {
        background-color: #161A21;
        border-radius: 12px;
        border: 1px solid #2D343F;
    }
    
    QLabel {
        color: #E6EDF3;
        font-family: 'Segoe UI', sans-serif;
    }
    
    QLabel#Title {
        font-size: 24px;
        font-weight: bold;
        color: #FFFFFF;
    }
    
    QLabel#Subtitle {
        font-size: 14px;
        color: #8B949E;
    }
    
    QLabel#CoreTemp {
        font-size: 32px;
        font-weight: 600;
        color: #58A6FF;
    }
    
    QFrame#CoreTile {
        background-color: #1C2128;
        border-radius: 8px;
        border: 1px solid #30363D;
        min-width: 140px;
        max-width: 180px;
        min-height: 120px;
    }
    
    QFrame#CoreTile[status="hot"] {
        border: 1px solid #F85149;
        background-color: #2D1A1A;
    }
    
    QFrame#CoreTile[status="warm"] {
        border: 1px solid #D29922;
    }
    
    QPushButton#ActionButton {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    
    QPushButton#ActionButton:hover {
        background-color: #2EA043;
    }
    """
