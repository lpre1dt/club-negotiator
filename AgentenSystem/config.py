# =================================================================
# FOOTBALL NEGOTIATION SYSTEM - ZENTRALE KONFIGURATION
# =================================================================

# =================================================================
# SYSTEM EINSTELLUNGEN
# =================================================================
SYSTEM_CONFIG = {
    # Anzahl Spieler die geladen werden sollen
    "MAX_PLAYERS": 30,
    # CSV-Datei Pfad
    "CSV_FILE_PATH": "player_stats.csv",
    # Erstelle automatisch Beispieldaten wenn CSV nicht existiert
    "AUTO_CREATE_SAMPLE_DATA": True,
    # Encoding für CSV-Dateien
    "CSV_ENCODING": "utf-8",
}

# =================================================================
# VERHANDLUNGS-PARAMETER
# =================================================================
NEGOTIATION_CONFIG = {
    # Maximale Anzahl Verhandlungsrunden
    "MAX_ROUNDS": 15000,
    # Anteil Team-Shuffle vs. einzelne Swaps (0.0 = nur Swaps, 1.0 = nur Shuffles)
    "TEAM_SHUFFLE_FREQUENCY": 0.01,  # Alle 100 Runden ein Shuffle
    # Prozentsatz der Spieler bei Team-Shuffle
    "SHUFFLE_PERCENTAGE": 0.2,
    # Fortschritts-Anzeige alle X akzeptierte Swaps
    "PROGRESS_INTERVAL_SWAPS": 250,
    # Fortschritts-Anzeige alle X Runden (falls wenige Swaps)
    "PROGRESS_INTERVAL_ROUNDS": 2000,
}

# =================================================================
# SIMULATED ANNEALING PARAMETER
# =================================================================
SA_CONFIG = {
    # Start-Temperatur
    "INITIAL_TEMPERATURE": 50.0,
    # Mindest-Akzeptanzrate während Kalibrierung
    "MIN_ACCEPTANCE_RATE": 0.8,
    # Maximum Iterationen für Simulated Annealing
    "MAX_ITERATIONS": 10000,
    # Anzahl Iterationen für Temperatur-Kalibrierung
    "CALIBRATION_ITERATIONS": 1000,
    # Minimum Temperatur (verhindert T = 0)
    "MIN_TEMPERATURE": 0.01,
    # Fallback Temperatur wenn Kalibrierung fehlschlägt
    "FALLBACK_TEMPERATURE": 10.0,
    # Mindest-Akzeptanzrate für Kalibrierung
    "MIN_CALIBRATION_RATE": 0.1,
}

# =================================================================
# KÄUFER-VEREIN KONFIGURATION (FC OFFENSIVE UNITED)
# =================================================================
BUYER_CONFIG = {
    "CLUB_NAME": "FC Offensive United",
    # Attribut-Gewichtungen (normalisiert auf 0-1)
    "ATTRIBUTE_WEIGHTS": {
        "ball_control": 2.5,  # Sehr wichtig für Technik
        "dribbling": 2.3,  # Sehr wichtig für Technik
        "slide_tackle": 0.5,  # Weniger wichtig
        "stand_tackle": 0.7,  # Weniger wichtig
        "aggression": 1.0,  # Neutral
        "reactions": 1.8,  # Wichtig
        "att_position": 2.8,  # Sehr wichtig für Offensive
        "interceptions": 1.2,  # Etwas wichtig
        "vision": 2.4,  # Sehr wichtig für Kreativität
        "composure": 2.0,  # Wichtig
        "crossing": 1.5,  # Wichtig
        "short_pass": 2.2,  # Sehr wichtig
        "long_pass": 1.8,  # Wichtig
        "acceleration": 2.1,  # Wichtig
        "stamina": 1.9,  # Wichtig
        "strength": 1.4,  # Etwas wichtig
        "balance": 1.7,  # Wichtig
        "sprint_speed": 2.0,  # Wichtig
        "agility": 2.2,  # Sehr wichtig
        "jumping": 1.3,  # Etwas wichtig
        "heading": 1.4,  # Etwas wichtig
        "shot_power": 2.6,  # Sehr wichtig
        "finishing": 2.9,  # Extrem wichtig für Tore
        "long_shots": 2.1,  # Wichtig
    },
    # Positions-Gewichtungen (Index = Position, Wert = Gewichtung)
    "POSITION_WEIGHTS": [
        # Defensive Positionen (0-9) - niedrigere Gewichtung
        0.8,
        0.8,
        0.9,
        0.9,
        1.0,
        1.1,
        1.1,
        1.2,
        1.2,
        1.3,
        # Mittelfeld (10-19) - mittlere Gewichtung
        1.4,
        1.4,
        1.5,
        1.5,
        1.6,
        1.7,
        1.7,
        1.8,
        1.8,
        1.9,
        # Angriff (20-29) - hohe Gewichtung
        2.0,
        2.1,
        2.2,
        2.3,
        2.4,
        2.5,
        2.6,
        2.7,
        2.8,
        2.9,
    ],
}

# =================================================================
# VERKÄUFER-VEREIN KONFIGURATION (DEFENSIVE FC)
# =================================================================
SELLER_CONFIG = {
    "CLUB_NAME": "Defensive FC",
    # Attribut-Gewichtungen (fokussiert auf Defensive)
    "ATTRIBUTE_WEIGHTS": {
        "ball_control": 1.9,  # Wichtig
        "dribbling": 1.5,  # Etwas wichtig
        "slide_tackle": 2.5,  # Sehr wichtig
        "stand_tackle": 2.7,  # Sehr wichtig
        "aggression": 1.8,  # Wichtig
        "reactions": 2.0,  # Wichtig
        "att_position": 1.2,  # Weniger wichtig
        "interceptions": 2.6,  # Sehr wichtig für Defense
        "vision": 1.7,  # Wichtig
        "composure": 1.8,  # Wichtig
        "crossing": 1.0,  # Weniger wichtig
        "short_pass": 2.1,  # Wichtig
        "long_pass": 1.9,  # Wichtig
        "acceleration": 1.8,  # Wichtig
        "stamina": 2.4,  # Sehr wichtig für Laufleistung
        "strength": 2.2,  # Wichtig für Defense
        "balance": 1.6,  # Wichtig
        "sprint_speed": 1.7,  # Wichtig
        "agility": 1.5,  # Wichtig
        "jumping": 1.9,  # Wichtig für Defense
        "heading": 2.3,  # Sehr wichtig für Defense
        "shot_power": 1.4,  # Etwas wichtig
        "finishing": 1.1,  # Weniger wichtig
        "long_shots": 1.3,  # Etwas wichtig
    },
    # Positions-Gewichtungen (hohe Gewichtung für Defense)
    "POSITION_WEIGHTS": [
        # Defensive Positionen (0-9) - hohe Gewichtung
        2.9,
        2.8,
        2.7,
        2.6,
        2.5,
        2.4,
        2.3,
        2.2,
        2.1,
        2.0,
        # Mittelfeld (10-19) - mittlere Gewichtung
        1.9,
        1.8,
        1.7,
        1.6,
        1.5,
        1.4,
        1.3,
        1.2,
        1.1,
        1.0,
        # Angriff (20-29) - niedrige Gewichtung
        0.9,
        0.9,
        0.8,
        0.8,
        0.8,
        0.7,
        0.7,
        0.6,
        0.6,
        0.5,
    ],
}

# =================================================================
# UTILITY-BERECHNUNG PARAMETER
# =================================================================
UTILITY_CONFIG = {
    # Gewichtung für Synergieeffekte
    "SYNERGY_WEIGHT": 10.0,
    # Gewichtung für Altersbonus
    "AGE_BONUS_WEIGHT": 1.0,
    # Ideales Durchschnittsalter für Teams
    "IDEAL_AVERAGE_AGE": 27,
    # Penalty pro Jahr Abweichung vom idealen Alter
    "AGE_PENALTY_PER_YEAR": 2.0,
    # Maximum Altersbonus
    "MAX_AGE_BONUS": 100.0,
    # Parameter für Pass-Synergie
    "MAX_PASS_SYNERGY": 10.0,
    "PASS_SYNERGY_THRESHOLD": 10.0,
    # Parameter für Alters-Synergie
    "MAX_AGE_SYNERGY": 5.0,
    "AGE_SYNERGY_DIVISOR": 3.0,
}

# =================================================================
# LOGGING UND OUTPUT KONFIGURATION
# =================================================================
LOGGING_CONFIG = {
    # Zeige Temperatur-Kalibrierung
    "SHOW_TEMPERATURE_CALIBRATION": True,
    # Zeige gelegentlich Temperatur während Verhandlung
    "SHOW_TEMPERATURE_UPDATES": True,
    "TEMPERATURE_UPDATE_INTERVAL": 1000,
    # Zeige detaillierte Start-Informationen
    "SHOW_DETAILED_START_INFO": True,
    # Anzahl Beispiel-Spieler am Start
    "NUM_EXAMPLE_PLAYERS": 5,
    # Anzahl Top-Spieler in Endergebnis
    "NUM_TOP_PLAYERS": 5,
    # Anzahl Beispiel-Wechsel pro Progress-Update
    "NUM_EXAMPLE_CHANGES": 3,
    # Zeige erweiterte Endergebnis-Statistiken
    "SHOW_EXTENDED_STATS": True,
    # Zeige Positions-Analyse
    "SHOW_POSITION_ANALYSIS": True,
    # Zeige Utility-Entwicklung
    "SHOW_UTILITY_DEVELOPMENT": True,
    # Zeige Team-Komposition-Analyse
    "SHOW_TEAM_COMPOSITION": True,
}

# =================================================================
# ADVANCED ANALYSIS KONFIGURATION
# =================================================================
ANALYSIS_CONFIG = {
    # Analysiere Top/Bottom Positionen
    "ANALYZE_POSITION_PREFERENCES": True,
    # Anzahl Positionen für Top/Bottom Analyse
    "NUM_POSITIONS_TO_ANALYZE": 10,
    # Analysiere Altersverteilung
    "ANALYZE_AGE_DISTRIBUTION": True,
    # Altersgruppen für Analyse
    "AGE_GROUPS": {"Young": (18, 23), "Prime": (24, 29), "Veteran": (30, 35)},
    # Analysiere Attribut-Verteilung
    "ANALYZE_ATTRIBUTE_DISTRIBUTION": True,
    # Wichtigste Attribute für Analyse
    "KEY_ATTRIBUTES": ["finishing", "vision", "stamina", "heading"],
    # Berechne Synergie-Statistiken
    "CALCULATE_SYNERGY_STATS": True,
    # Zeige Verhandlungs-Historie
    "SHOW_NEGOTIATION_HISTORY": True,
    # Intervall für Verhandlungs-Historie (jeder X-te Swap)
    "HISTORY_INTERVAL": 500,
}

# =================================================================
# EXPORT KONFIGURATION
# =================================================================
EXPORT_CONFIG = {
    # Exportiere Endergebnisse nach CSV
    "EXPORT_RESULTS_TO_CSV": False,
    # Pfad für Export-CSV
    "EXPORT_PATH": "negotiation_results.csv",
    # Exportiere Verhandlungs-Historie
    "EXPORT_HISTORY": False,
    # Pfad für Verhandlungs-Historie
    "HISTORY_PATH": "negotiation_history.csv",
}

# =================================================================
# VALIDATION UND DEBUGGING
# =================================================================
DEBUG_CONFIG = {
    # Validiere Konfiguration beim Start
    "VALIDATE_CONFIG": True,
    # Zeige Konfigurations-Übersicht
    "SHOW_CONFIG_SUMMARY": False,
    # Debug Modus (zusätzliche Ausgaben)
    "DEBUG_MODE": False,
    # Speichere Debug-Logs
    "SAVE_DEBUG_LOGS": False,
    # Pfad für Debug-Logs
    "DEBUG_LOG_PATH": "debug.log",
}
