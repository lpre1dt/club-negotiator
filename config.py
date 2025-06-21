# =================================================================
# FOOTBALL NEGOTIATION SYSTEM - ZENTRALE KONFIGURATION
# Erweitert für echte Vereine aus CSV
# =================================================================

# =================================================================
# SYSTEM EINSTELLUNGEN
# =================================================================
SYSTEM_CONFIG = {
    # CSV-Datei Pfad
    "CSV_FILE_PATH": "player_stats.csv",
    # CSV Encoding
    "CSV_ENCODING": "iso-8859-1",  # ISO-8859-1 für europäische Zeichen
    # Minimale Spieleranzahl pro Verein für Verhandlungen
    "MIN_PLAYERS_PER_CLUB": 11,
    # Maximale Spieleranzahl pro Verein (für Performance)
    "MAX_PLAYERS_PER_CLUB": 50,
    # Erstelle automatisch Beispieldaten wenn CSV nicht existiert
    "AUTO_CREATE_SAMPLE_DATA": False,
    # Filtere Spieler ohne wichtige Attribute
    "FILTER_INVALID_PLAYERS": True,
}

# =================================================================
# VERHANDLUNGS-PARAMETER
# =================================================================
NEGOTIATION_CONFIG = {
    # Maximale Anzahl Verhandlungsrunden
    "MAX_ROUNDS": 5000,
    # Minimale Kadergröße pro Verein
    "MIN_SQUAD_SIZE": 11,
    # Maximale Transfers pro Verein
    "MAX_TRANSFERS_PER_CLUB": 10,
    # Anteil Team-Shuffle vs. einzelne Swaps
    "TEAM_SHUFFLE_FREQUENCY": 0.05,  # Alle 20 Runden ein Shuffle
    # Prozentsatz der Spieler bei Team-Shuffle
    "SHUFFLE_PERCENTAGE": 0.3,
    # Fortschritts-Anzeige alle X akzeptierte Swaps
    "PROGRESS_INTERVAL_SWAPS": 100,
    # Fortschritts-Anzeige alle X Runden
    "PROGRESS_INTERVAL_ROUNDS": 500,
    # Erlaube Transfers zwischen verschiedenen Ligen
    "ALLOW_INTER_LEAGUE_TRANSFERS": True,
    # Transfer-Gebühren-Simulation
    "SIMULATE_TRANSFER_FEES": False,
}

# =================================================================
# SIMULATED ANNEALING PARAMETER
# =================================================================
SA_CONFIG = {
    # Start-Temperatur
    "INITIAL_TEMPERATURE": 100.0,
    # Mindest-Akzeptanzrate während Kalibrierung
    "MIN_ACCEPTANCE_RATE": 0.7,
    # Maximum Iterationen für Simulated Annealing
    "MAX_ITERATIONS": 5000,
    # Anzahl Iterationen für Temperatur-Kalibrierung
    "CALIBRATION_ITERATIONS": 500,
    # Minimum Temperatur
    "MIN_TEMPERATURE": 0.01,
    # Fallback Temperatur wenn Kalibrierung fehlschlägt
    "FALLBACK_TEMPERATURE": 20.0,
    # Mindest-Akzeptanzrate für Kalibrierung
    "MIN_CALIBRATION_RATE": 0.2,
    # Temperatur-Abkühlrate
    "COOLING_RATE": 0.95,
}

# =================================================================
# STRATEGIE-SPEZIFISCHE KONFIGURATIONEN
# =================================================================
STRATEGY_CONFIG = {
    "offensive": {
        "ATTRIBUTE_MULTIPLIERS": {
            "finishing": 1.8,
            "shot_power": 1.6,
            "att_position": 1.7,
            "dribbling": 1.5,
            "acceleration": 1.5,
            "sprint_speed": 1.4,
            "agility": 1.4,
            "ball_control": 1.3,
            "long_shots": 1.3,
        },
        "POSITION_PREFERENCE": "ATT",
        "AGE_PREFERENCE": "young",  # young, balanced, experienced
    },
    "defensive": {
        "ATTRIBUTE_MULTIPLIERS": {
            "slide_tackle": 1.8,
            "stand_tackle": 1.8,
            "interceptions": 1.7,
            "heading": 1.6,
            "strength": 1.5,
            "stamina": 1.5,
            "jumping": 1.4,
            "aggression": 1.3,
            "reactions": 1.3,
        },
        "POSITION_PREFERENCE": "DEF",
        "AGE_PREFERENCE": "experienced",
    },
    "balanced": {
        "ATTRIBUTE_MULTIPLIERS": {
            # Alle Attribute gleich gewichtet
        },
        "POSITION_PREFERENCE": "ANY",
        "AGE_PREFERENCE": "balanced",
    },
    "technical": {
        "ATTRIBUTE_MULTIPLIERS": {
            "ball_control": 1.8,
            "vision": 1.8,
            "short_pass": 1.7,
            "long_pass": 1.6,
            "composure": 1.6,
            "dribbling": 1.5,
            "crossing": 1.4,
            "agility": 1.3,
            "balance": 1.3,
        },
        "POSITION_PREFERENCE": "MID",
        "AGE_PREFERENCE": "balanced",
    },
}

# =================================================================
# UTILITY-BERECHNUNG PARAMETER
# =================================================================
UTILITY_CONFIG = {
    # Basis-Gewichtungen
    "BASE_ATTRIBUTE_WEIGHT": 1.0,
    "POSITION_MATCH_BONUS": 50.0,
    "WRONG_POSITION_PENALTY": -30.0,
    
    # Synergieeffekte
    "SYNERGY_WEIGHT": 5.0,
    "SAME_CLUB_SYNERGY": 20.0,
    "SAME_COUNTRY_SYNERGY": 10.0,
    "CHEMISTRY_THRESHOLD": 10,  # Differenz für gute Chemie
    
    # Altersbonus
    "AGE_BONUS_WEIGHT": 2.0,
    "IDEAL_AVERAGE_AGE": 26,
    "AGE_PENALTY_PER_YEAR": 3.0,
    "MAX_AGE_BONUS": 50.0,
    
    # Spieler-Wert Integration
    "VALUE_WEIGHT": 0.1,  # Wie stark der Marktwert einbezogen wird
    
    # Team-Balance
    "BALANCE_BONUS": 30.0,  # Bonus für ausgewogene Teams
    "POSITION_DISTRIBUTION": {
        "GK": (0.05, 0.1),   # (min, max) Anteil
        "DEF": (0.3, 0.4),
        "MID": (0.3, 0.4),
        "ATT": (0.2, 0.3),
    },
}

# =================================================================
# TRANSFER MARKT KONFIGURATION
# =================================================================
TRANSFER_CONFIG = {
    # Transfer-Wahrscheinlichkeiten
    "BASE_TRANSFER_PROBABILITY": 0.1,
    "SAME_LEAGUE_MULTIPLIER": 1.5,
    "RIVAL_CLUB_PENALTY": 0.3,
    
    # Transfer-Fenster Simulation
    "SIMULATE_TRANSFER_WINDOWS": False,
    "WINTER_WINDOW_ACTIVITY": 0.5,  # Reduzierte Aktivität im Winter
    
    # Spieler-Präferenzen
    "PLAYER_LOYALTY_FACTOR": 0.2,  # Wie ungern Spieler wechseln
    "BIG_CLUB_ATTRACTION": 1.5,    # Attraktivität großer Vereine
    
    # Finanzielle Aspekte (wenn aktiviert)
    "BUDGET_CONSTRAINTS": False,
    "DEFAULT_CLUB_BUDGET": 50_000_000,
    "WAGE_BUDGET_RATIO": 0.5,
}

# =================================================================
# LOGGING UND OUTPUT KONFIGURATION
# =================================================================
LOGGING_CONFIG = {
    # Zeige Temperatur-Kalibrierung
    "SHOW_TEMPERATURE_CALIBRATION": True,
    # Zeige Transfer-Details
    "SHOW_TRANSFER_DETAILS": True,
    # Anzahl Beispiel-Spieler in Ausgaben
    "NUM_EXAMPLE_PLAYERS": 5,
    # Anzahl Top-Transfers in Zusammenfassung
    "NUM_TOP_TRANSFERS": 10,
    # Zeige Team-Statistiken
    "SHOW_TEAM_STATS": True,
    # Zeige Positions-Verteilung
    "SHOW_POSITION_DISTRIBUTION": True,
    # Export Transfer-Historie
    "EXPORT_TRANSFER_HISTORY": True,
}

# =================================================================
# STREAMLIT UI KONFIGURATION
# =================================================================
UI_CONFIG = {
    # Theme
    "THEME": "light",
    # Zeige erweiterte Optionen
    "SHOW_ADVANCED_OPTIONS": True,
    # Standard-Ansicht
    "DEFAULT_VIEW": "clubs",  # clubs, players, transfers
    # Animations
    "ENABLE_ANIMATIONS": True,
    # Charts
    "CHART_HEIGHT": 400,
    "CHART_WIDTH": 600,
    # Farben für Strategien
    "STRATEGY_COLORS": {
        "offensive": "#FF6B6B",
        "defensive": "#4ECDC4",
        "balanced": "#95E1D3",
        "technical": "#A8E6CF",
    },
}

# =================================================================
# DATENANALYSE KONFIGURATION
# =================================================================
ANALYSIS_CONFIG = {
    # Analysiere Vereins-Stärken
    "ANALYZE_CLUB_STRENGTHS": True,
    # Vergleiche vor/nach Transfers
    "COMPARE_BEFORE_AFTER": True,
    # Berechne Transfer-Effizienz
    "CALCULATE_TRANSFER_EFFICIENCY": True,
    # Wichtigste Attribute für Analyse
    "KEY_ATTRIBUTES": [
        "finishing", "vision", "stamina", "heading",
        "ball_control", "short_pass", "slide_tackle", "sprint_speed"
    ],
    # Positions-Gruppen für Analyse
    "POSITION_GROUPS": {
        "Offensive": ["ST", "CF", "LW", "RW"],
        "Midfield": ["CM", "CAM", "CDM", "LM", "RM"],
        "Defensive": ["CB", "LB", "RB", "LWB", "RWB"],
        "Goalkeeper": ["GK"],
    },
}

# =================================================================
# PERFORMANCE KONFIGURATION
# =================================================================
PERFORMANCE_CONFIG = {
    # Multi-Threading für große Datenmengen
    "USE_MULTIPROCESSING": False,
    "MAX_WORKERS": 4,
    # Caching
    "ENABLE_CACHING": True,
    "CACHE_SIZE": 1000,
    # Batch-Verarbeitung
    "BATCH_SIZE": 100,
    # Memory Management
    "MAX_MEMORY_MB": 500,
}

# =================================================================
# EXPORT KONFIGURATION
# =================================================================
EXPORT_CONFIG = {
    # Dateiformate
    "EXPORT_FORMAT": "csv",  # csv, json, excel
    # Pfade
    "TRANSFER_HISTORY_PATH": "transfer_history.csv",
    "TEAM_ANALYSIS_PATH": "team_analysis.csv",
    "NEGOTIATION_REPORT_PATH": "negotiation_report.pdf",
    # Inhalt
    "INCLUDE_PLAYER_DETAILS": True,
    "INCLUDE_FINANCIAL_DATA": False,
    "INCLUDE_PERFORMANCE_METRICS": True,
}

# =================================================================
# VALIDATION UND DEBUGGING
# =================================================================
DEBUG_CONFIG = {
    # Validiere Konfiguration beim Start
    "VALIDATE_CONFIG": True,
    # Validiere Spielerdaten
    "VALIDATE_PLAYER_DATA": True,
    # Debug Modus
    "DEBUG_MODE": False,
    # Verbose Logging
    "VERBOSE_LOGGING": False,
    # Speichere Debug-Logs
    "SAVE_DEBUG_LOGS": False,
    "DEBUG_LOG_PATH": "debug.log",
    # Performance Profiling
    "ENABLE_PROFILING": False,
}