# PlayerDataLoader.py - Korrigiert für Semikolon-getrennte CSV
import csv
from typing import List, Dict, Tuple
from PlayerAgent import Player

# Sichere config imports
try:
    from config import SYSTEM_CONFIG
except ImportError:
    SYSTEM_CONFIG = {
        "CSV_FILE_PATH": "player_stats.csv",
        "CSV_ENCODING": "iso-8859-1",
        "MAX_PLAYERS": 30,
        "MIN_PLAYERS_PER_CLUB": 11,
        "AUTO_CREATE_SAMPLE_DATA": True
    }

from data_class import fix_mojibake


class PlayerDataLoader:
    """
    Lädt Spielerdaten aus CSV-Dateien mit Vereinszuordnung
    """

    @staticmethod
    def load_players_by_club(file_path: str = None, 
                           encoding: str = "iso-8859-1") -> Dict[str, List[Player]]:
        """
        Lädt Spielerdaten und gruppiert sie nach Vereinen
        
        WICHTIG: Verwendet Semikolon (;) als Trennzeichen!
        
        Returns:
            Dict[str, List[Player]]: Dictionary mit Vereinsnamen als Keys und Spielerlisten als Values
        """
        if file_path is None:
            file_path = SYSTEM_CONFIG.get("CSV_FILE_PATH", "player_stats.csv")
        
        players_by_club = {}
        
        try:
            # WICHTIG: delimiter=';' für Semikolon-getrennte CSV!
            with open(file_path, "r", encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter=';')  # <-- HIER IST DIE WICHTIGE ÄNDERUNG!
                
                for row_num, row in enumerate(reader):
                    try:
                        # Bereinige Encoding-Probleme
                        cleaned_row = {}
                        for key, value in row.items():
                            if key and value:  # Prüfe ob key und value existieren
                                if isinstance(value, str):
                                    value = fix_mojibake(value)
                                cleaned_row[key] = value
                        
                        # Bereinige die Daten
                        cleaned_row = PlayerDataLoader._clean_row(cleaned_row)
                        
                        # Extrahiere Vereinsnamen
                        club_name = cleaned_row.get("club", "").strip()
                        if not club_name or club_name == "Unknown" or club_name == "":
                            continue
                            
                        # Erstelle Spieler
                        player_name = cleaned_row.get("player", "").strip()
                        if not player_name or player_name == "Unknown":
                            continue
                            
                        player = Player(player_name, cleaned_row)
                        
                        # Füge Spieler zum Verein hinzu
                        if club_name not in players_by_club:
                            players_by_club[club_name] = []
                        players_by_club[club_name].append(player)
                        
                    except Exception as e:
                        # Zeige Fehler nur für die ersten paar Zeilen
                        if row_num < 5:
                            print(f"Fehler in Zeile {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Fehler: Datei nicht gefunden: {file_path}")
            raise
        except Exception as e:
            print(f"Fehler beim Laden der CSV: {e}")
            print("Tipp: Prüfe ob die CSV Semikolon-getrennt ist")
            raise
            
        return players_by_club

    @staticmethod
    def get_clubs_with_min_players(players_by_club: Dict[str, List[Player]], 
                                  min_players: int = 11) -> List[str]:
        """
        Gibt Liste von Vereinen zurück, die mindestens min_players Spieler haben
        """
        return [club for club, players in players_by_club.items() 
                if len(players) >= min_players]

    @staticmethod
    def load_from_csv(file_path: str = None, max_players: int = None) -> List[Player]:
        """
        Lädt Spielerdaten aus einer CSV-Datei (alte Methode für Kompatibilität)
        
        WICHTIG: Verwendet Semikolon (;) als Trennzeichen!

        Args:
            file_path: Pfad zur CSV-Datei
            max_players: Maximale Anzahl zu ladender Spieler

        Returns:
            List[Player]: Liste der geladenen Spieler
        """
        if file_path is None:
            file_path = SYSTEM_CONFIG.get("CSV_FILE_PATH", "player_stats.csv")
        if max_players is None:
            max_players = SYSTEM_CONFIG.get("MAX_PLAYERS", 30)

        players = []
        encoding = SYSTEM_CONFIG.get("CSV_ENCODING", "iso-8859-1")

        try:
            # WICHTIG: delimiter=';' für Semikolon-getrennte CSV!
            with open(file_path, "r", encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter=';')  # <-- AUCH HIER!

                for i, row in enumerate(reader):
                    if max_players and i >= max_players:
                        break

                    try:
                        # Bereinige die Daten
                        cleaned_row = PlayerDataLoader._clean_row(row)

                        # Erstelle Spieler-Objekt
                        player_name = cleaned_row.get("player", "Unknown").strip()
                        if player_name and player_name != "Unknown":
                            player = Player(player_name, cleaned_row)
                            players.append(player)
                    except Exception as e:
                        if i < 5:  # Zeige nur erste Fehler
                            print(f"Fehler bei Spieler {i}: {e}")
                        continue

        except FileNotFoundError:
            print(f"Fehler: Datei nicht gefunden: {file_path}")
            if SYSTEM_CONFIG.get("AUTO_CREATE_SAMPLE_DATA", True):
                print("Erstelle automatisch Beispieldaten...")
                return PlayerDataLoader._create_sample_players(max_players)
            else:
                raise
        except Exception as e:
            print(f"Fehler beim Laden der CSV: {e}")
            raise

        return players

    @staticmethod
    def _clean_row(row: Dict[str, str]) -> Dict[str, str]:
        """
        Bereinigt eine Datenzeile und ersetzt leere Werte
        """
        cleaned = {}

        for key, value in row.items():
            if not key:  # Skip wenn key leer
                continue
                
            # Entferne Leerzeichen
            key = key.strip()
            value = value.strip() if value else "0"

            # Encoding-Probleme beheben
            if isinstance(value, str):
                value = fix_mojibake(value)

            # Ersetze leere Werte mit Standardwerten
            if not value or value == "" or value == "nan" or value == "NaN":
                if key in ["player", "country", "club"]:
                    value = "Unknown"
                else:
                    value = "0"

            cleaned[key] = value

        return cleaned

    @staticmethod
    def _create_sample_players(num_players: int) -> List[Player]:
        """
        Erstellt Beispiel-Spieler basierend auf Konfiguration
        """
        import random

        # Konfigurierbare Listen
        sample_names = [
            "Max Mustermann", "John Smith", "Carlos Rodriguez", "Luca Rossi",
            "Pierre Dubois", "Ahmed Hassan", "Hiroshi Tanaka", "Lars Andersen",
            "Miguel Santos", "Stefan Mueller", "Kevin O'Connor", "Antonio Silva",
            "Johan van der Berg", "Piotr Kowalski", "Ivan Petrov"
        ]

        countries = [
            "Germany", "England", "Spain", "Italy", "France", "Brazil",
            "Argentina", "Netherlands", "Belgium", "Portugal"
        ]

        clubs = [
            "FC Barcelona", "Real Madrid", "Manchester United", "Bayern Munich",
            "Liverpool", "Paris SG", "Juventus", "AC Milan", "Arsenal", "Chelsea"
        ]

        players = []

        for i in range(num_players):
            # Wähle zufälligen Namen
            base_name = random.choice(sample_names)
            name = f"{base_name} {i+1}"

            # Zufällige aber realistische Attribute
            data = {
                "player": name,
                "country": random.choice(countries),
                "height": str(random.randint(165, 195)),
                "weight": str(random.randint(65, 90)),
                "age": str(random.randint(18, 35)),
                "club": random.choice(clubs),
                "value": f"{random.randint(100, 5000)}.000",
                # Technische Fertigkeiten
                "ball_control": str(random.randint(40, 95)),
                "dribbling": str(random.randint(30, 90)),
                "vision": str(random.randint(35, 95)),
                "composure": str(random.randint(40, 90)),
                "short_pass": str(random.randint(45, 95)),
                "long_pass": str(random.randint(30, 90)),
                # Defensive Fertigkeiten
                "slide_tackle": str(random.randint(20, 80)),
                "stand_tackle": str(random.randint(25, 85)),
                "interceptions": str(random.randint(30, 85)),
                "heading": str(random.randint(30, 85)),
                # Physische Attribute
                "acceleration": str(random.randint(40, 95)),
                "sprint_speed": str(random.randint(40, 95)),
                "stamina": str(random.randint(55, 95)),
                "strength": str(random.randint(45, 90)),
                "balance": str(random.randint(50, 90)),
                "agility": str(random.randint(45, 90)),
                "jumping": str(random.randint(35, 85)),
                # Mentale Attribute
                "aggression": str(random.randint(35, 90)),
                "reactions": str(random.randint(45, 95)),
                # Offensive Attribute
                "att_position": str(random.randint(25, 90)),
                "crossing": str(random.randint(25, 85)),
                "shot_power": str(random.randint(25, 90)),
                "finishing": str(random.randint(20, 90)),
                "long_shots": str(random.randint(25, 85)),
                # Weitere Attribute
                "curve": str(random.randint(20, 85)),
                "fk_acc": str(random.randint(20, 85)),
                "penalties": str(random.randint(30, 90)),
                "volleys": str(random.randint(20, 80)),
                # Torwart (meist niedrig für Feldspieler)
                "gk_positioning": str(random.randint(5, 20)),
                "gk_diving": str(random.randint(5, 20)),
                "gk_handling": str(random.randint(5, 20)),
                "gk_kicking": str(random.randint(5, 20)),
                "gk_reflexes": str(random.randint(5, 20))
            }

            player = Player(name, data)
            players.append(player)

        print(f"Erstellt {num_players} Beispiel-Spieler")
        return players

    @staticmethod
    def save_sample_csv(file_path: str = None, num_players: int = None):
        """
        Erstellt eine Beispiel-CSV-Datei mit SEMIKOLON als Trennzeichen
        """
        if file_path is None:
            file_path = SYSTEM_CONFIG.get("CSV_FILE_PATH", "player_stats.csv")
        if num_players is None:
            num_players = SYSTEM_CONFIG.get("MAX_PLAYERS", 30)

        players = PlayerDataLoader._create_sample_players(num_players)

        headers = [
            "player", "country", "height", "weight", "age", "club",
            "ball_control", "dribbling", "slide_tackle", "stand_tackle",
            "aggression", "reactions", "att_position", "interceptions",
            "vision", "composure", "crossing", "short_pass", "long_pass",
            "acceleration", "stamina", "strength", "balance", "sprint_speed",
            "agility", "jumping", "heading", "shot_power", "finishing",
            "long_shots", "curve", "fk_acc", "penalties", "volleys",
            "gk_positioning", "gk_diving", "gk_handling", "gk_kicking",
            "gk_reflexes", "value"
        ]

        encoding = SYSTEM_CONFIG.get("CSV_ENCODING", "utf-8")

        # WICHTIG: delimiter=';' beim Schreiben!
        with open(file_path, "w", newline="", encoding=encoding) as file:
            writer = csv.writer(file, delimiter=';')  # <-- Semikolon!
            writer.writerow(headers)

            for player in players:
                row = [
                    player.name, player.country,
                    180, 75,  # height, weight
                    player.age, player.club,
                    player.ball_control, player.dribbling,
                    player.slide_tackle, player.stand_tackle,
                    player.aggression, player.reactions,
                    player.att_position, player.interceptions,
                    player.vision, player.composure,
                    player.crossing, player.short_pass, player.long_pass,
                    player.acceleration, player.stamina,
                    player.strength, player.balance,
                    player.sprint_speed, player.agility,
                    player.jumping, player.heading,
                    player.shot_power, player.finishing,
                    player.long_shots,
                    50, 50, 50, 50,  # curve, fk_acc, penalties, volleys
                    10, 10, 10, 10, 10,  # gk attributes
                    f"{player.value:.0f}"
                ]
                writer.writerow(row)

        print(f"Beispiel-CSV erstellt: {file_path}")