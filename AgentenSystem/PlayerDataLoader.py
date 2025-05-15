import csv
from typing import List, Dict
from PlayerAgent import Player
from config import SYSTEM_CONFIG


class PlayerDataLoader:
    """
    Lädt Spielerdaten aus CSV-Dateien - vollständig konfigurierbar
    """

    @staticmethod
    def load_from_csv(file_path: str = None, max_players: int = None) -> List[Player]:
        """
        Lädt Spielerdaten aus einer CSV-Datei

        Args:
            file_path: Pfad zur CSV-Datei (falls None, aus Konfiguration)
            max_players: Maximale Anzahl zu ladender Spieler (falls None, aus Konfiguration)

        Returns:
            List[Player]: Liste der geladenen Spieler
        """
        # Verwende Konfigurationswerte als Standard
        if file_path is None:
            file_path = SYSTEM_CONFIG.get("CSV_FILE_PATH", "player_stats.csv")
        if max_players is None:
            max_players = SYSTEM_CONFIG.get("MAX_PLAYERS", 30)

        players = []
        encoding = SYSTEM_CONFIG.get("CSV_ENCODING", "utf-8")

        try:
            with open(file_path, "r", encoding=encoding) as file:
                reader = csv.DictReader(file)

                for i, row in enumerate(reader):
                    if max_players and i >= max_players:
                        break

                    # Bereinige die Daten
                    cleaned_row = PlayerDataLoader._clean_row(row)

                    # Erstelle Spieler-Objekt
                    player = Player(cleaned_row["player"], cleaned_row)
                    players.append(player)

        except FileNotFoundError:
            print(f"Fehler: Datei nicht gefunden: {file_path}")
            # Auto-Create basierend auf Konfiguration
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
            # Entferne Leerzeichen
            key = key.strip()
            value = value.strip() if value else "0"

            # Ersetze leere Werte mit Standardwerten
            if not value or value == "" or value == "nan":
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
            "Max Mustermann",
            "John Smith",
            "Carlos Rodriguez",
            "Luca Rossi",
            "Pierre Dubois",
            "Ahmed Hassan",
            "Hiroshi Tanaka",
            "Lars Andersen",
            "Miguel Santos",
            "Stefan Mueller",
            "Kevin O'Connor",
            "Antonio Silva",
            "Johan van der Berg",
            "Piotr Kowalski",
            "Ivan Petrov",
            "Marco Bianchi",
            "Jean-Luc Martin",
            "Giuseppe Verdi",
            "Hans Schmidt",
            "Erik Johnson",
            "Francisco Garcia",
            "Roberto Fernandez",
            "Giovanni Rossi",
            "Hans Weber",
            "Jean Dupont",
            "Mohammed Ali",
            "Yuki Tanaka",
            "Ole Nielsen",
        ]

        countries = [
            "Germany",
            "England",
            "Spain",
            "Italy",
            "France",
            "Brazil",
            "Argentina",
            "Netherlands",
            "Belgium",
            "Portugal",
            "Mexico",
            "USA",
            "Japan",
            "Sweden",
            "Denmark",
            "Poland",
        ]

        clubs = [
            "FC Barcelona",
            "Real Madrid",
            "Manchester United",
            "Bayern Munich",
            "Liverpool",
            "Paris SG",
            "Juventus",
            "AC Milan",
            "Arsenal",
            "Chelsea",
            "Manchester City",
            "Atletico Madrid",
            "Borussia Dortmund",
            "Inter Milan",
            "Tottenham",
            "Napoli",
            "Roma",
            "Sevilla",
            "Villarreal",
            "Leicester City",
        ]

        players = []

        for i in range(num_players):
            # Wähle zufälligen Namen und stelle Eindeutigkeit sicher
            base_name = random.choice(sample_names)
            name = f"{base_name} {i+1}"

            # Zufällige aber realistische Attribute mit realistischeren Verteilungen
            data = {
                "country": random.choice(countries),
                "age": random.randint(18, 35),
                "club": random.choice(clubs),
                "value": f"${random.randint(100, 5000)}.000",
                # Technische Fertigkeiten (meist höher)
                "ball_control": random.randint(40, 95),
                "dribbling": random.randint(30, 90),
                "vision": random.randint(35, 95),
                "composure": random.randint(40, 90),
                "short_pass": random.randint(45, 95),
                "long_pass": random.randint(30, 90),
                # Defensive Fertigkeiten
                "slide_tackle": random.randint(20, 80),
                "stand_tackle": random.randint(25, 85),
                "interceptions": random.randint(30, 85),
                "heading": random.randint(30, 85),
                # Physische Attribute
                "acceleration": random.randint(40, 95),
                "sprint_speed": random.randint(40, 95),
                "stamina": random.randint(55, 95),
                "strength": random.randint(45, 90),
                "balance": random.randint(50, 90),
                "agility": random.randint(45, 90),
                "jumping": random.randint(35, 85),
                # Mentale Attribute
                "aggression": random.randint(35, 90),
                "reactions": random.randint(45, 95),
                # Offensive Attribute
                "att_position": random.randint(25, 90),
                "crossing": random.randint(25, 85),
                "shot_power": random.randint(25, 90),
                "finishing": random.randint(20, 90),
                "long_shots": random.randint(25, 85),
            }

            player = Player(name, data)
            players.append(player)

        print(f"Erstellt {num_players} konfigurierbare Beispiel-Spieler")
        return players

    @staticmethod
    def save_sample_csv(file_path: str = None, num_players: int = None):
        """
        Erstellt eine Beispiel-CSV-Datei basierend auf Konfiguration
        """
        if file_path is None:
            file_path = SYSTEM_CONFIG.get("CSV_FILE_PATH", "player_stats.csv")
        if num_players is None:
            num_players = SYSTEM_CONFIG.get("MAX_PLAYERS", 30)

        players = PlayerDataLoader._create_sample_players(num_players)

        headers = [
            "player",
            "country",
            "height",
            "weight",
            "age",
            "club",
            "ball_control",
            "dribbling",
            "slide_tackle",
            "stand_tackle",
            "aggression",
            "reactions",
            "att_position",
            "interceptions",
            "vision",
            "composure",
            "crossing",
            "short_pass",
            "long_pass",
            "acceleration",
            "stamina",
            "strength",
            "balance",
            "sprint_speed",
            "agility",
            "jumping",
            "heading",
            "shot_power",
            "finishing",
            "long_shots",
            "curve",
            "fk_acc",
            "penalties",
            "volleys",
            "gk_positioning",
            "gk_diving",
            "gk_handling",
            "gk_kicking",
            "gk_reflexes",
            "value",
        ]

        encoding = SYSTEM_CONFIG.get("CSV_ENCODING", "utf-8")

        with open(file_path, "w", newline="", encoding=encoding) as file:
            writer = csv.writer(file)
            writer.writeheader()

            for player in players:
                row = [
                    player.name,
                    player.country,
                    180,
                    75,
                    player.age,
                    player.club,
                    player.ball_control,
                    player.dribbling,
                    player.slide_tackle,
                    player.stand_tackle,
                    player.aggression,
                    player.reactions,
                    player.att_position,
                    player.interceptions,
                    player.vision,
                    player.composure,
                    player.crossing,
                    player.short_pass,
                    player.long_pass,
                    player.acceleration,
                    player.stamina,
                    player.strength,
                    player.balance,
                    player.sprint_speed,
                    player.agility,
                    player.jumping,
                    player.heading,
                    player.shot_power,
                    player.finishing,
                    player.long_shots,
                    50,
                    50,
                    50,
                    50,
                    10,
                    10,
                    10,
                    10,
                    10,
                    f"${player.value:,.0f}",
                ]
                writer.writerow(row)

        print(f"Konfigurierbare Beispiel-CSV erstellt: {file_path}")
