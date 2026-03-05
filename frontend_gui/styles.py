def get_application_styles():
    return """
    /* --- GLOBAL WINDOW & BACKGROUND --- */
    QMainWindow, QWidget#CentralWidget {
        background-color: #1A1A1A;  /* Modern Dark Gray (Not pure black) */
        color: #F0F0F0;
        font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
    }
    
    QScrollArea {
        border: none;
        background-color: transparent;
    }

    /* --- TYPOGRAPHY --- */
    QLabel {
        color: #E0E0E0;
        font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
    }
    
    /* Huge Headline for 5-Second Rule */
    QLabel#HeroTitle {
        font-size: 28px; /* Reduced from 42px to prevent clipping */
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    /* Section Headers */
    QLabel#SectionHeader {
        font-size: 16px;
        font-weight: 600;
        color: #A0A0A0; /* Muted */
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Standard Text */
    QLabel#BodyText {
        font-size: 14px;
        color: #CCCCCC;
        line-height: 1.4;
    }
    
    /* Small Captions */
    QLabel#Caption {
        font-size: 11px;
        color: #808080;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* Big Metrics */
    QLabel#MetricValue {
        font-size: 28px; /* Reduced from 36px to prevent clipping */
        font-weight: 700; 
        color: #00D1B2; /* Default Teal */
    }

    /* --- CONTAINERS & PANELS --- */
    /* Glass / Card Effect */
    QFrame#Panel {
        background-color: rgba(40, 40, 40, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    QFrame#Panel:hover {
        background-color: rgba(50, 50, 50, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    /* Highlight Panel (e.g., Active Migration) */
    QFrame#HighlightPanel {
        background-color: rgba(0, 122, 204, 0.15); /* VS Blue Tint */
        border-radius: 12px;
        border: 1px solid rgba(0, 122, 204, 0.3);
    }

    /* --- BUTTONS & INTERACTION --- */
    QPushButton {
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        color: #E0E0E0;
        padding: 8px 16px;
        font-weight: 600;
    }
    
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    QPushButton:pressed {
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* --- NAVIGATION --- */
    /* Tab Bar Style */
    QFrame#NavBar {
        background-color: #252526;
        border-bottom: 1px solid rgba(0,0,0,0.5);
    }
    
    QPushButton#NavButton {
        background-color: transparent;
        border: none;
        border-radius: 0px;
        color: #909090;
        font-size: 14px;
        font-weight: 500;
        padding: 12px 20px;
        text-align: left;
    }
    
    QPushButton#NavButton:hover {
        color: #FFFFFF;
        background-color: rgba(255,255,255,0.05);
    }
    
    QPushButton#NavButton[active="true"] {
        color: #FFFFFF;
        border-left: 3px solid #007ACC; /* Blue accent on left */
        background-color: rgba(0, 122, 204, 0.1);
        font-weight: 700;
    }

    /* --- CORE TILES (Modern) --- */
    QFrame#CoreZone {
        background-color: rgba(30, 30, 30, 0.8);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Status Colors - Backgrounds & Borders */
    /* SAFE (Teal/Green) */
    QFrame#CoreZone[status="safe"] {
        background-color: rgba(0, 209, 178, 0.25); 
        border: 1px solid rgba(0, 209, 178, 0.5);
        border-bottom: 3px solid rgba(0, 209, 178, 0.8);
    }
    QFrame#CoreZone[status="safe"]:hover {
        background-color: rgba(0, 209, 178, 0.35);
        border: 1px solid rgba(0, 209, 178, 0.8);
    }

    /* WARM (Amber) */
    QFrame#CoreZone[status="warm"] {
        background-color: rgba(255, 193, 7, 0.25);
        border: 1px solid rgba(255, 193, 7, 0.5);
        border-bottom: 3px solid rgba(255, 193, 7, 0.8);
    }
    QFrame#CoreZone[status="warm"]:hover {
        background-color: rgba(255, 193, 7, 0.35);
        border: 1px solid rgba(255, 193, 7, 0.8);
    }

    /* HOT (Red) */
    QFrame#CoreZone[status="hot"] {
        background-color: rgba(220, 53, 69, 0.3);
        border: 1px solid rgba(220, 53, 69, 0.6);
        border-bottom: 3px solid rgba(220, 53, 69, 0.9);
    }
    QFrame#CoreZone[status="hot"]:hover {
        background-color: rgba(220, 53, 69, 0.4);
        border: 1px solid rgba(220, 53, 69, 1.0);
    }

    /* --- PROGRESS BARS --- */
    QProgressBar {
        border: none;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        height: 6px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #007ACC;
        border-radius: 4px;
    }
    """

