"""
Zentrale Konfigurationsdatei für das Fußball-Verhandlungssystem.

Diese Datei enthält alle wichtigen Einstellungen, die das Verhalten des Systems
steuern, von Datenquellen über Club-Strategien bis hin zu Verhandlungsparametern
und Logging-Optionen. Die Konfigurationen sind in thematische Diktionaries
unterteilt, um eine klare Struktur und einfache Anpassbarkeit zu gewährleisten.

Hauptbereiche der Konfiguration:
- SYSTEM_CONFIG: Allgemeine Systemeinstellungen wie Dateipfade und Encodings.
- CLUB_CONFIG: Auswahl und Management der verhandelnden Clubs.
- DISPLAY_CONFIG: Einstellungen für die Anzeige von Informationen während der Simulation.
- NEGOTIATION_CONFIG: Parameter, die den Verhandlungsablauf steuern.
- SA_CONFIG: Einstellungen für den Simulated Annealing Algorithmus der Agenten.
- BUYER_CONFIG: Spezifische Strategie-Gewichtungen für den Käufer-Club.
- SELLER_CONFIG: Spezifische Strategie-Gewichtungen für den Verkäufer-Club.
- UTILITY_CONFIG: Parameter für die Berechnung von Team-Utility und Boni.
- LOGGING_CONFIG: Einstellungen für das Logging und die Ausgabe von Informationen.
- ANALYSIS_CONFIG: Konfigurationen für erweiterte Analysefunktionen.
- EXPORT_CONFIG: Einstellungen für den Export von Ergebnissen.
- DEBUG_CONFIG: Parameter für Debugging und Validierung.

Die Funktion `validate_club_config` dient zur Überprüfung der Club-bezogenen
Einstellungen auf Gültigkeit und Konsistenz.
"""

# =================================================================
# SYSTEMEINSTELLUNGEN
# Definiert grundlegende Systemeinstellungen.
# =================================================================
SYSTEM_CONFIG = {
    # Pfad zur CSV-Datei mit Spielerdaten.
    "CSV_FILE_PATH": "player_stats.csv",
    # Zeichenkodierung für das Einlesen von CSV-Dateien (z.B. "utf-8", "latin1").
    "CSV_ENCODING": "latin1",
    # Legt fest, ob automatisch Beispieldaten generiert werden sollen,
    # falls die angegebene CSV-Datei nicht existiert.
    "AUTO_CREATE_SAMPLE_DATA": True,
}

# =================================================================
# CLUB-AUSWAHL UND MANAGEMENT
# Konfiguration für die Auswahl und das Management der verhandelnden Clubs.
# =================================================================
CLUB_CONFIG = {
    # Name des Käufer-Clubs. Muss exakt mit einem Eintrag in der CSV-Spalte "club" übereinstimmen.
    "BUYER_CLUB_NAME": "River Plate",
    # Name des Verkäufer-Clubs. Muss exakt mit einem Eintrag in der CSV-Spalte "club" übereinstimmen.
    "SELLER_CLUB_NAME": "Liverpool",
    
    # Mindestanzahl an Spielern, die ein Club haben muss, um an Verhandlungen teilzunehmen.
    "MIN_PLAYERS_REQUIRED": 11,  # Entspricht einer Startelf.
    
    # Strategie zur Behandlung von unterschiedlich großen Kadern:
    # - "pad_smaller": Füllt den kleineren Kader mit Dummy-Spielern auf die Größe des größeren Kaders auf.
    # - "truncate_larger": Kürzt den größeren Kader auf die Größe des kleineren Kaders.
    # - "use_minimum": Verwendet von beiden Kadern nur die Anzahl Spieler des kleinsten Kaders.
    # - "allow_unequal": Erlaubt Verhandlungen mit unterschiedlich großen Kadern (kann komplex sein).
    "SQUAD_SIZE_STRATEGY": "use_minimum",
    
    # Name für Dummy-Spieler, falls die Strategie "pad_smaller" verwendet wird.
    "DUMMY_PLAYER_NAME": "Reserve Player",
    
    # Maximale Anzahl an Spielern pro Club, um übermäßig große Kader zu limitieren.
    "MAX_PLAYERS_PER_CLUB": 30,
    
    # Legt fest, ob bei nicht auffindbaren Clubs auf Beispieldaten zurückgegriffen werden soll.
    "FALLBACK_TO_SAMPLE_DATA": True,
}

# =================================================================
# ANZEIGEKONFIGURATION
# Steuert, welche Informationen während der Simulation angezeigt werden.
# =================================================================
DISPLAY_CONFIG = {
    # Zeigt detaillierte Informationen über die Clubs (z.B. Name, Anzahl Spieler).
    "SHOW_CLUB_DETAILS": True,
    # Zeigt die (normalerweise verborgenen) Zielfunktionen und Strategien der Clubs.
    "SHOW_CLUB_OBJECTIVES": True,
    # Zeigt die anfängliche Kaderzusammensetzung vor Beginn der Verhandlungen.
    "SHOW_INITIAL_SQUADS": True,
    # Anzahl der Beispiel-Spieler, die pro Club angezeigt werden (z.B. in Statistiken).
    "NUM_EXAMPLE_PLAYERS_PER_CLUB": 5,
    # Zeigt Statistiken über die Spielerverteilung (z.B. Durchschnittsalter).
    "SHOW_PLAYER_STATISTICS": True,
    # Gibt Warnungen aus, wenn Probleme mit den Kadergrößen auftreten (z.B. zu wenige Spieler).
    "WARN_SQUAD_SIZE_ISSUES": True,
}

# =================================================================
# VERHANDLUNGSPARAMETER
# Parameter, die den Ablauf und die Dynamik der Verhandlungen bestimmen.
# =================================================================
NEGOTIATION_CONFIG = {
    # Maximale Anzahl an Verhandlungsrunden, die durchgeführt werden.
    "MAX_ROUNDS": 15000,
    # Frequenz von "Team Shuffle"-Vorschlägen im Verhältnis zu einzelnen Spieler-Swaps.
    # 0.0 bedeutet nur Swaps, 1.0 bedeutet nur Shuffles. 0.01 = ca. alle 100 Runden ein Shuffle.
    "TEAM_SHUFFLE_FREQUENCY": 0.01,
    # Prozentsatz der Spieler, die bei einem "Team Shuffle" neu gemischt werden.
    "SHUFFLE_PERCENTAGE": 0.2,
    # Intervall (Anzahl akzeptierter Swaps), in dem Fortschrittsinformationen angezeigt werden.
    "PROGRESS_INTERVAL_SWAPS": 250,
    # Intervall (Anzahl Runden), in dem Fortschrittsinformationen angezeigt werden,
    # falls nur wenige Swaps akzeptiert wurden.
    "PROGRESS_INTERVAL_ROUNDS": 2000,
}

# =================================================================
# SIMULATED ANNEALING PARAMETER
# Parameter für den Simulated Annealing Algorithmus, den die Agenten zur Entscheidungsfindung nutzen.
# =================================================================
SA_CONFIG = {
    # Anfangstemperatur für den Simulated Annealing Prozess.
    "INITIAL_TEMPERATURE": 50.0,
    # Mindestakzeptanzrate, die während der Kalibrierungsphase des SA erreicht werden soll.
    "MIN_ACCEPTANCE_RATE": 0.8,
    # Maximale Anzahl an Iterationen (Runden) für den gesamten SA-Prozess.
    "MAX_ITERATIONS": 10000,
    # Anzahl der initialen Iterationen, die zur Kalibrierung der Temperatur verwendet werden.
    "CALIBRATION_ITERATIONS": 1000,
    # Minimaltemperatur, die der SA-Prozess nicht unterschreiten soll (verhindert T=0).
    "MIN_TEMPERATURE": 0.01,
    # Fallback-Temperatur, falls die Kalibrierung fehlschlägt (z.B. wenn avg_delta = 0).
    "FALLBACK_TEMPERATURE": 10.0,
    # Mindestakzeptanzrate, die für die Temperaturberechnung während der Kalibrierung verwendet wird.
    "MIN_CALIBRATION_RATE": 0.1,
}

# =================================================================
# KÄUFER-CLUB SPEZIFISCHE KONFIGURATION
# Definiert die Strategie und Präferenzen des Käufer-Clubs.
# =================================================================
BUYER_CONFIG = {
    # Optional: Überschreibt den Club-Namen aus CLUB_CONFIG.
    # Falls None, wird der Name aus CLUB_CONFIG["BUYER_CLUB_NAME"] verwendet.
    "CLUB_NAME": None,  
    
    # Gewichtungen für einzelne Spielerattribute. Höhere Werte bedeuten höhere Priorität.
    # Diese Gewichtungen definieren die "geheime" Präferenz des Käufers.
    # Beispiel: Käufer bevorzugt offensive und technisch starke Spieler.
    "ATTRIBUTE_WEIGHTS": {
        "ball_control": 2.5,  # Sehr wichtig für Technik
        "dribbling": 2.3,     # Sehr wichtig für Technik
        "slide_tackle": 0.5,  # Weniger wichtig für Käufer-Strategie
        "stand_tackle": 0.7,  # Weniger wichtig für Käufer-Strategie
        "aggression": 1.0,    # Neutral bewertet
        "reactions": 1.8,     # Wichtig für schnelles Reagieren
        "att_position": 2.8,  # Sehr wichtig für offensive Positionierung
        "interceptions": 1.2, # Etwas wichtig für Balleroberung
        "vision": 2.4,        # Sehr wichtig für kreatives Passspiel
        "composure": 2.0,     # Wichtig für Gelassenheit unter Druck
        "crossing": 1.5,      # Wichtig für Flanken
        "short_pass": 2.2,    # Sehr wichtig für Kurzpassspiel
        "long_pass": 1.8,     # Wichtig für lange Pässe
        "acceleration": 2.1,  # Wichtig für Antrittsschnelligkeit
        "stamina": 1.9,       # Wichtig für Ausdauer
        "strength": 1.4,      # Etwas wichtig für körperliche Stärke
        "balance": 1.7,       # Wichtig für Gleichgewicht
        "sprint_speed": 2.0,  # Wichtig für Endgeschwindigkeit
        "agility": 2.2,       # Sehr wichtig für Beweglichkeit
        "jumping": 1.3,       # Etwas wichtig für Sprungkraft
        "heading": 1.4,       # Etwas wichtig für Kopfballspiel
        "shot_power": 2.6,    # Sehr wichtig für Schusskraft
        "finishing": 2.9,     # Extrem wichtig für Torabschluss
        "long_shots": 2.1,    # Wichtig für Weitschüsse
    },
    # Gewichtungen für Positionen im Kader (Index-basiert).
    # Definiert, wie wichtig Spieler auf bestimmten Positionen im Kader sind.
    # Frühe Indizes (z.B. 0-10) repräsentieren oft Stammspieler.
    "POSITION_WEIGHTS": [
        # Beispiel: Frühe Positionen (0-9) - mittlere Gewichtung
        1.8, 1.8, 1.7, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1,
        # Beispiel: Mittlere Positionen (10-19) - niedrige Gewichtung
        1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1,
        # Beispiel: Späte Positionen (20-29) - sehr niedrige Gewichtung (z.B. Reserve)
        0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
    ],
}

# =================================================================
# VERKÄUFER-CLUB SPEZIFISCHE KONFIGURATION
# Definiert die Strategie und Präferenzen des Verkäufer-Clubs.
# =================================================================
SELLER_CONFIG = {
    # Optional: Überschreibt den Club-Namen aus CLUB_CONFIG.
    # Falls None, wird der Name aus CLUB_CONFIG["SELLER_CLUB_NAME"] verwendet.
    "CLUB_NAME": None,  
    
    # Gewichtungen für Spielerattribute. Höhere Werte bedeuten höhere Priorität.
    # Beispiel: Verkäufer fokussiert sich auf defensive Stabilität und Laufleistung.
    "ATTRIBUTE_WEIGHTS": {
        "ball_control": 1.9,  # Wichtig
        "dribbling": 1.5,     # Etwas wichtig
        "slide_tackle": 2.5,  # Sehr wichtig für Defensive
        "stand_tackle": 2.7,  # Sehr wichtig für Defensive
        "aggression": 1.8,    # Wichtig für Zweikampfhärte
        "reactions": 2.0,     # Wichtig für schnelles Reagieren
        "att_position": 1.2,  # Weniger wichtig für Verkäufer-Strategie
        "interceptions": 2.6, # Sehr wichtig für Balleroberung in der Defensive
        "vision": 1.7,        # Wichtig für Spielübersicht
        "composure": 1.8,     # Wichtig für Gelassenheit
        "crossing": 1.0,      # Weniger wichtig
        "short_pass": 2.1,    # Wichtig für sicheres Passspiel
        "long_pass": 1.9,     # Wichtig für Spieleröffnung
        "acceleration": 1.8,  # Wichtig
        "stamina": 2.4,       # Sehr wichtig für hohe Laufleistung
        "strength": 2.2,      # Wichtig für körperliche Robustheit in der Defensive
        "balance": 1.6,       # Wichtig
        "sprint_speed": 1.7,  # Wichtig
        "agility": 1.5,       # Wichtig
        "jumping": 1.9,       # Wichtig für Kopfballduelle in der Defensive
        "heading": 2.3,       # Sehr wichtig für Kopfballspiel (defensiv & offensiv)
        "shot_power": 1.4,    # Etwas wichtig
        "finishing": 1.1,     # Weniger wichtig
        "long_shots": 1.3,    # Etwas wichtig
    },
    # Gewichtungen für Positionen im Kader.
    # Beispiel: Verkäufer möchte seine besten Spieler auf frühen Positionen halten/bewerten.
    "POSITION_WEIGHTS": [
        # Beispiel: Frühe Positionen (0-9) - hohe Gewichtung
        2.9, 2.8, 2.7, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0,
        # Beispiel: Mittlere Positionen (10-19) - mittlere Gewichtung
        1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0,
        # Beispiel: Späte Positionen (20-29) - niedrige Gewichtung
        0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05,
    ],
}

# =================================================================
# PARAMETER FÜR UTILITY-BERECHNUNG
# Einstellungen für die Berechnung von Boni und Synergien in der Utility-Funktion.
# =================================================================
UTILITY_CONFIG = {
    # Gewichtungsfaktor für den gesamten Synergiebonus.
    "SYNERGY_WEIGHT": 10.0,
    # Gewichtungsfaktor für den Altersbonus.
    "AGE_BONUS_WEIGHT": 1.0,
    # Ideales Durchschnittsalter eines Teams, das zu einem Bonus führt.
    "IDEAL_AVERAGE_AGE": 27,
    # Strafe pro Jahr Abweichung vom idealen Durchschnittsalter.
    "AGE_PENALTY_PER_YEAR": 2.0,
    # Maximaler Bonus, der für die Altersstruktur erreicht werden kann.
    "MAX_AGE_BONUS": 100.0,
    # Maximaler Bonus für Pass-Synergie zwischen zwei benachbarten Spielern.
    "MAX_PASS_SYNERGY": 10.0,
    # Schwellenwert für Pass-Differenz; größere Differenzen reduzieren den Synergiebonus.
    "PASS_SYNERGY_THRESHOLD": 10.0,
    # Maximaler Bonus für Alters-Synergie zwischen zwei benachbarten Spielern.
    "MAX_AGE_SYNERGY": 5.0,
    # Divisor zur Skalierung des Altersunterschieds für die Alters-Synergie.
    "AGE_SYNERGY_DIVISOR": 3.0,
}

# =================================================================
# LOGGING UND AUSGABEKONFIGURATION
# Steuert, welche Informationen während der Simulation geloggt und ausgegeben werden.
# =================================================================
LOGGING_CONFIG = {
    # Zeigt detaillierte Informationen zur Temperaturkalibrierung des SA-Algorithmus.
    "SHOW_TEMPERATURE_CALIBRATION": True,
    # Zeigt periodische Updates der Temperatur während der Verhandlung.
    "SHOW_TEMPERATURE_UPDATES": True,
    # Intervall (Anzahl Runden) für die Anzeige von Temperatur-Updates.
    "TEMPERATURE_UPDATE_INTERVAL": 1000,
    # Zeigt detaillierte Startinformationen, einschließlich Spieler-Bewertungs-Previews.
    "SHOW_DETAILED_START_INFO": True,
    # Anzahl der Beispiel-Spieler, die zu Beginn der Simulation angezeigt werden.
    "NUM_EXAMPLE_PLAYERS": 5,
    # Anzahl der Top-Spieler, die im Endergebnis hervorgehoben werden.
    "NUM_TOP_PLAYERS": 5,
    # Anzahl der Beispiel-Änderungen (Swaps/Trades), die bei Fortschritts-Updates angezeigt werden.
    "NUM_EXAMPLE_CHANGES": 3,
    # Zeigt erweiterte Statistiken im Endergebnis der Verhandlung.
    "SHOW_EXTENDED_STATS": True,
    # Zeigt eine Analyse der bevorzugten Positionen der Agenten.
    "SHOW_POSITION_ANALYSIS": True,
    # Zeigt die Entwicklung der Utility-Werte über die Zeit (z.B. als Plot).
    "SHOW_UTILITY_DEVELOPMENT": True,
    # Zeigt eine Analyse der finalen Team-Zusammensetzung.
    "SHOW_TEAM_COMPOSITION": True,
}

# =================================================================
# ERWEITERTE ANALYSEKONFIGURATION
# Einstellungen für detailliertere Analysen des Verhandlungsprozesses und -ergebnisses.
# =================================================================
ANALYSIS_CONFIG = {
    # Analysiert die Präferenzen der Agenten für Top-/Bottom-Positionen im Kader.
    "ANALYZE_POSITION_PREFERENCES": True,
    # Anzahl der Positionen, die für die Top-/Bottom-Analyse berücksichtigt werden.
    "NUM_POSITIONS_TO_ANALYZE": 10,
    # Analysiert die Altersverteilung in den finalen Kadern.
    "ANALYZE_AGE_DISTRIBUTION": True,
    # Definiert Altersgruppen für die Analyse der Altersverteilung.
    "AGE_GROUPS": {"Young": (18, 23), "Prime": (24, 29), "Veteran": (30, 35)},
    # Analysiert die Verteilung wichtiger Spielerattribute in den finalen Kadern.
    "ANALYZE_ATTRIBUTE_DISTRIBUTION": True,
    # Liste der Schlüsselattribute, die für die Attribut-Verteilungsanalyse verwendet werden.
    "KEY_ATTRIBUTES": ["finishing", "vision", "stamina", "heading"],
    # Berechnet und zeigt Statistiken zu Synergieeffekten in den Teams.
    "CALCULATE_SYNERGY_STATS": True,
    # Zeigt die Historie der Verhandlungsentscheidungen (Trade Log).
    "SHOW_NEGOTIATION_HISTORY": True,
    # Intervall (Anzahl akzeptierter Swaps/Trades) für die Speicherung/Anzeige der Verhandlungshistorie.
    "HISTORY_INTERVAL": 500,
}

# =================================================================
# EXPORTKONFIGURATION
# Einstellungen für den Export von Verhandlungsergebnissen und -daten.
# =================================================================
EXPORT_CONFIG = {
    # Legt fest, ob die finalen Kaderzusammensetzungen als CSV-Datei exportiert werden sollen.
    "EXPORT_RESULTS_TO_CSV": False,
    # Standardpfad für die exportierte CSV-Datei mit den Endergebnissen.
    "EXPORT_PATH": "negotiation_results.csv",
    # Legt fest, ob die detaillierte Verhandlungshistorie (Trade Log) exportiert werden soll.
    "EXPORT_HISTORY": False,
    # Standardpfad für die exportierte CSV-Datei mit der Verhandlungshistorie.
    "HISTORY_PATH": "negotiation_history.csv",
}

# =================================================================
# VALIDIERUNGS- UND DEBUGGING-KONFIGURATION
# Einstellungen zur Unterstützung bei der Fehlersuche und Validierung.
# =================================================================
DEBUG_CONFIG = {
    # Führt beim Start eine Validierung der Konfigurationseinstellungen durch (siehe `validate_club_config`).
    "VALIDATE_CONFIG": True,
    # Zeigt eine Zusammenfassung der geladenen Konfiguration beim Start an.
    "SHOW_CONFIG_SUMMARY": False,
    # Aktiviert den Debug-Modus, der zusätzliche, detailliertere Ausgaben erzeugt.
    "DEBUG_MODE": False,
    # Legt fest, ob Debug-Logs in eine Datei gespeichert werden sollen.
    "SAVE_DEBUG_LOGS": False,
    # Pfad zur Datei, in der Debug-Logs gespeichert werden, falls `SAVE_DEBUG_LOGS` True ist.
    "DEBUG_LOG_PATH": "debug.log",
}

# =================================================================
# CLUB-SPEZIFISCHE VALIDIERUNGSFUNKTION
# Dient zur Überprüfung der Korrektheit und Konsistenz der Club-Konfigurationen.
# =================================================================
def validate_club_config():
    """
    Validiert die Club-Konfiguration (CLUB_CONFIG) und gibt Warnungen aus,
    falls Inkonsistenzen oder fehlende Werte festgestellt werden.

    Returns:
        bool: True, wenn keine Warnungen gefunden wurden, andernfalls False.
    """
    warnings = []  # Liste zum Sammeln von Warnmeldungen
    
    # Prüfe, ob die Namen der verhandelnden Clubs gesetzt sind.
    if not CLUB_CONFIG.get("BUYER_CLUB_NAME"): # .get() für mehr Sicherheit
        warnings.append("⚠️ BUYER_CLUB_NAME ist nicht gesetzt oder leer!")
    
    if not CLUB_CONFIG.get("SELLER_CLUB_NAME"):
        warnings.append("⚠️ SELLER_CLUB_NAME ist nicht gesetzt oder leer!")
    
    # Prüfe die Gültigkeit der gewählten Strategie für Kadergrößen.
    valid_strategies = ["pad_smaller", "truncate_larger", "use_minimum", "allow_unequal"]
    if CLUB_CONFIG.get("SQUAD_SIZE_STRATEGY") not in valid_strategies:
        warnings.append(f"⚠️ Ungültige SQUAD_SIZE_STRATEGY: {CLUB_CONFIG.get('SQUAD_SIZE_STRATEGY')}")
        warnings.append(f"   Gültige Optionen sind: {valid_strategies}")
    
    # Gib gesammelte Warnungen aus, falls vorhanden und Validierung aktiviert ist.
    if warnings and DEBUG_CONFIG.get("VALIDATE_CONFIG", True):
        print("\n" + "="*50)
        print("KONFIGURATIONS-WARNUNGEN (config.py):")
        print("="*50)
        for warning in warnings:
            print(warning)
        print("="*50 + "\n")
    
    return len(warnings) == 0 # True, wenn keine Warnungen, sonst False