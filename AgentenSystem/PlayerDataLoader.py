import csv
from typing import List, Dict, Tuple, Optional
from PlayerAgent import Player
from config import SYSTEM_CONFIG, CLUB_CONFIG, DISPLAY_CONFIG


class ClubBasedPlayerDataLoader:
    """
    Lädt Spielerdaten aus CSV-Dateien mit Club-basierter Auswahl
    
    Das neue System:
    1. Lädt alle Spieler aus der CSV
    2. Filtert nach den konfigurierten Club-Namen  
    3. Behandelt unterschiedliche Squad-Größen intelligent
    4. Validiert die Ergebnisse
    """

    @staticmethod
    def load_clubs_from_csv(
        buyer_club_name: str = None, 
        seller_club_name: str = None,
        file_path: str = None
    ) -> Tuple[List[Player], List[Player]]:
        """
        Lädt Spielerdaten für zwei spezifische Clubs aus der CSV
        
        Args:
            buyer_club_name: Name des Käufer-Clubs (aus CSV)
            seller_club_name: Name des Verkäufer-Clubs (aus CSV)  
            file_path: Pfad zur CSV-Datei
            
        Returns:
            Tuple[List[Player], List[Player]]: (Käufer-Spieler, Verkäufer-Spieler)
            
        Raises:
            FileNotFoundError: Wenn CSV nicht gefunden wird
            ValueError: Wenn Club nicht genügend Spieler hat
        """
        # Lade Konfiguration falls Parameter nicht gesetzt
        if buyer_club_name is None:
            buyer_club_name = CLUB_CONFIG["BUYER_CLUB_NAME"]
        if seller_club_name is None:
            seller_club_name = CLUB_CONFIG["SELLER_CLUB_NAME"]
        if file_path is None:
            file_path = SYSTEM_CONFIG["CSV_FILE_PATH"]
        
        print("=" * 70)
        print("CLUB-BASIERTE SPIELER-AUSWAHL")
        print("=" * 70)
        print(f"CSV Datei: {file_path}")
        print(f"Käufer Club: {buyer_club_name}")
        print(f"Verkäufer Club: {seller_club_name}")
        print()
        
        try:
            # 1. Lade alle Spieler aus der CSV
            all_players = ClubBasedPlayerDataLoader._load_all_players_from_csv(file_path)
            
            # 2. Filtere nach Club-Namen
            buyer_players = ClubBasedPlayerDataLoader._filter_players_by_club(
                all_players, buyer_club_name
            )
            seller_players = ClubBasedPlayerDataLoader._filter_players_by_club(
                all_players, seller_club_name
            )
            
            # 3. Zeige Statistiken
            ClubBasedPlayerDataLoader._print_club_statistics(
                buyer_club_name, buyer_players, seller_club_name, seller_players
            )
            
            # 4. Validiere Squad-Größen
            ClubBasedPlayerDataLoader._validate_squad_sizes(
                buyer_club_name, buyer_players, seller_club_name, seller_players
            )
            
            # 5. Behandle unterschiedliche Squad-Größen
            buyer_players, seller_players = ClubBasedPlayerDataLoader._handle_squad_size_differences(
                buyer_club_name, buyer_players, seller_club_name, seller_players
            )
            
            # 6. Finale Validierung und Info
            ClubBasedPlayerDataLoader._print_final_squad_info(
                buyer_club_name, buyer_players, seller_club_name, seller_players
            )
            
            return buyer_players, seller_players
            
        except FileNotFoundError:
            print(f"❌ Fehler: CSV-Datei nicht gefunden: {file_path}")
            
            # Fallback zu Beispieldaten?
            if CLUB_CONFIG.get("FALLBACK_TO_SAMPLE_DATA", True):
                print("🔄 Erstelle Beispieldaten für beide Clubs...")
                return ClubBasedPlayerDataLoader._create_sample_clubs(
                    buyer_club_name, seller_club_name
                )
            else:
                raise
    
    @staticmethod
    def _load_all_players_from_csv(file_path: str) -> List[Player]:
        """
        Lädt alle Spieler aus der CSV-Datei
        
        Args:
            file_path: Pfad zur CSV-Datei
            
        Returns:
            List[Player]: Alle Spieler aus der CSV
        """
        players = []
        encoding = SYSTEM_CONFIG.get("CSV_ENCODING", "utf-8")
        
        print("🔄 Lade alle Spieler aus CSV...")
        
        with open(file_path, "r", encoding=encoding) as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Bereinige die Daten
                    cleaned_row = ClubBasedPlayerDataLoader._clean_row(row)
                    
                    # Erstelle Spieler-Objekt
                    player = Player(cleaned_row["player"], cleaned_row)
                    players.append(player)
                    
                except Exception as e:
                    print(f"⚠️ Warnung: Fehler in Zeile {row_num}: {e}")
                    continue
        
        print(f"✅ {len(players)} Spieler erfolgreich geladen")
        return players
    
    @staticmethod
    def _filter_players_by_club(players: List[Player], club_name: str) -> List[Player]:
        """
        Filtert Spieler nach Club-Namen
        
        Args:
            players: Liste aller Spieler
            club_name: Name des Clubs zum Filtern
            
        Returns:
            List[Player]: Spieler die zu diesem Club gehören
        """
        # Exakte Übereinstimmung
        exact_matches = [p for p in players if p.club == club_name]
        
        if exact_matches:
            return exact_matches
        
        # Falls keine exakte Übereinstimmung: Suche ähnliche Namen
        print(f"⚠️ Warnung: Keine exakte Übereinstimmung für '{club_name}'")
        print("   Suche nach ähnlichen Club-Namen...")
        
        # Case-insensitive Suche
        similar_matches = [
            p for p in players 
            if club_name.lower() in p.club.lower() or p.club.lower() in club_name.lower()
        ]
        
        if similar_matches:
            found_clubs = set(p.club for p in similar_matches)
            print(f"   Gefundene ähnliche Clubs: {found_clubs}")
            print(f"   Verwende ersten gefundenen Club: {list(found_clubs)[0]}")
            return [p for p in similar_matches if p.club == list(found_clubs)[0]]
        
        # Als letzte Option: Alle verfügbaren Clubs anzeigen
        available_clubs = set(p.club for p in players)
        print(f"❌ Club '{club_name}' nicht gefunden!")
        print(f"   Verfügbare Clubs: {sorted(available_clubs)}")
        
        return []
    
    @staticmethod
    def _print_club_statistics(
        buyer_name: str, buyer_players: List[Player],
        seller_name: str, seller_players: List[Player]
    ):
        """
        Zeigt Statistiken über die geladenen Club-Squads
        """
        if not DISPLAY_CONFIG.get("SHOW_PLAYER_STATISTICS", True):
            return
        
        print("\n📊 CLUB-SQUAD STATISTIKEN:")
        print("-" * 50)
        
        # Basis-Statistiken
        print(f"{buyer_name}:")
        print(f"  Anzahl Spieler: {len(buyer_players)}")
        if buyer_players:
            ages = [p.age for p in buyer_players]
            print(f"  Durchschnittsalter: {sum(ages)/len(ages):.1f} Jahre")
            print(f"  Altersbereich: {min(ages)}-{max(ages)} Jahre")
        
        print(f"\n{seller_name}:")
        print(f"  Anzahl Spieler: {len(seller_players)}")
        if seller_players:
            ages = [p.age for p in seller_players]
            print(f"  Durchschnittsalter: {sum(ages)/len(ages):.1f} Jahre")
            print(f"  Altersbereich: {min(ages)}-{max(ages)} Jahre")
        
        # Beispiel-Spieler
        num_examples = DISPLAY_CONFIG.get("NUM_EXAMPLE_PLAYERS_PER_CLUB", 5)
        
        if buyer_players and num_examples > 0:
            print(f"\nBeispiel-Spieler {buyer_name}:")
            for i, player in enumerate(buyer_players[:num_examples]):
                print(f"  {i+1}. {player.name} ({player.age} Jahre)")
        
        if seller_players and num_examples > 0:
            print(f"\nBeispiel-Spieler {seller_name}:")
            for i, player in enumerate(seller_players[:num_examples]):
                print(f"  {i+1}. {player.name} ({player.age} Jahre)")
    
    @staticmethod
    def _validate_squad_sizes(
        buyer_name: str, buyer_players: List[Player],
        seller_name: str, seller_players: List[Player]
    ):
        """
        Validiert ob die Squads die Mindestanforderungen erfüllen
        
        Raises:
            ValueError: Wenn ein Squad zu klein ist
        """
        min_players = CLUB_CONFIG["MIN_PLAYERS_REQUIRED"]
        
        issues = []
        
        if len(buyer_players) < min_players:
            issues.append(f"{buyer_name} hat nur {len(buyer_players)} Spieler (Minimum: {min_players})")
        
        if len(seller_players) < min_players:
            issues.append(f"{seller_name} hat nur {len(seller_players)} Spieler (Minimum: {min_players})")
        
        if issues and DISPLAY_CONFIG.get("WARN_SQUAD_SIZE_ISSUES", True):
            print("\n⚠️ SQUAD-GRÖSSEN PROBLEME:")
            for issue in issues:
                print(f"   {issue}")
            
            if not CLUB_CONFIG.get("FALLBACK_TO_SAMPLE_DATA", True):
                raise ValueError(f"Squad-Größen-Validierung fehlgeschlagen: {issues}")
    
    @staticmethod  
    def _handle_squad_size_differences(
        buyer_name: str, buyer_players: List[Player],
        seller_name: str, seller_players: List[Player]
    ) -> Tuple[List[Player], List[Player]]:
        """
        Behandelt unterschiedliche Squad-Größen basierend auf der Konfiguration
        
        Es gibt vier Strategien:
        1. "pad_smaller": Füllt den kleineren Squad mit Dummy-Spielern auf
        2. "truncate_larger": Kürzt den größeren Squad auf die kleinere Größe
        3. "use_minimum": Nimmt nur die ersten N Spieler beider Squads
        4. "allow_unequal": Erlaubt unterschiedliche Squad-Größen
        
        Returns:
            Tuple[List[Player], List[Player]]: Behandelte Squads
        """
        strategy = CLUB_CONFIG["SQUAD_SIZE_STRATEGY"]
        max_players = CLUB_CONFIG["MAX_PLAYERS_PER_CLUB"]
        
        # Limitiere zuerst auf Maximum
        if len(buyer_players) > max_players:
            print(f"✂️ Kürze {buyer_name} auf {max_players} Spieler")
            buyer_players = buyer_players[:max_players]
        
        if len(seller_players) > max_players:
            print(f"✂️ Kürze {seller_name} auf {max_players} Spieler")
            seller_players = seller_players[:max_players]
        
        # Wenn Squads bereits gleich groß sind, nichts tun
        if len(buyer_players) == len(seller_players):
            print(f"✅ Squad-Größen sind bereits identisch: {len(buyer_players)} Spieler")
            return buyer_players, seller_players
        
        print(f"\n🔧 SQUAD-GRÖßEN ANPASSUNG:")
        print(f"Strategie: {strategy}")
        print(f"Vor Anpassung: {buyer_name}={len(buyer_players)}, {seller_name}={len(seller_players)}")
        
        if strategy == "pad_smaller":
            # Fülle kleineren Squad mit Dummy-Spielern auf
            buyer_players, seller_players = ClubBasedPlayerDataLoader._pad_smaller_squad(
                buyer_name, buyer_players, seller_name, seller_players
            )
            
        elif strategy == "truncate_larger":
            # Kürze größeren Squad auf kleinere Größe
            min_size = min(len(buyer_players), len(seller_players))
            print(f"Kürze beide Squads auf {min_size} Spieler")
            buyer_players = buyer_players[:min_size]
            seller_players = seller_players[:min_size]
            
        elif strategy == "use_minimum":
            # Nimm nur die ersten N Spieler beider Squads
            min_size = min(len(buyer_players), len(seller_players))
            print(f"Verwende die ersten {min_size} Spieler beider Squads")
            buyer_players = buyer_players[:min_size]
            seller_players = seller_players[:min_size]
            
        elif strategy == "allow_unequal":
            # Erlaube unterschiedliche Squad-Größen
            print("Behalte unterschiedliche Squad-Größen bei")
            print("⚠️ Warnung: Dies kann zu Problemen in der Verhandlung führen!")
            
        else:
            raise ValueError(f"Unbekannte Squad-Size-Strategie: {strategy}")
        
        print(f"Nach Anpassung: {buyer_name}={len(buyer_players)}, {seller_name}={len(seller_players)}")
        
        return buyer_players, seller_players
    
    @staticmethod
    def _pad_smaller_squad(
        buyer_name: str, buyer_players: List[Player],
        seller_name: str, seller_players: List[Player]
    ) -> Tuple[List[Player], List[Player]]:
        """
        Füllt den kleineren Squad mit Dummy-Spielern auf
        
        Diese Dummy-Spieler haben minimale Attribute und dienen nur zum
        Auffüllen, damit beide Teams gleich viele "Positionen" haben.
        """
        if len(buyer_players) < len(seller_players):
            # Buyer-Squad ist kleiner
            deficit = len(seller_players) - len(buyer_players)
            print(f"Fülle {buyer_name} mit {deficit} Dummy-Spielern auf")
            
            for i in range(deficit):
                dummy_player = ClubBasedPlayerDataLoader._create_dummy_player(
                    f"{CLUB_CONFIG['DUMMY_PLAYER_NAME']} {i+1}", buyer_name
                )
                buyer_players.append(dummy_player)
                
        else:
            # Seller-Squad ist kleiner
            deficit = len(buyer_players) - len(seller_players)
            print(f"Fülle {seller_name} mit {deficit} Dummy-Spielern auf")
            
            for i in range(deficit):
                dummy_player = ClubBasedPlayerDataLoader._create_dummy_player(
                    f"{CLUB_CONFIG['DUMMY_PLAYER_NAME']} {i+1}", seller_name
                )
                seller_players.append(dummy_player)
        
        return buyer_players, seller_players
    
    @staticmethod
    def _create_dummy_player(name: str, club: str) -> Player:
        """
        Erstellt einen Dummy-Spieler mit minimalen Attributen
        
        Args:
            name: Name des Dummy-Spielers
            club: Club des Dummy-Spielers
            
        Returns:
            Player: Dummy-Player mit niedrigen Attributen
        """
        # Minimale Attribute für Dummy-Spieler
        dummy_data = {
            "country": "Unknown",
            "age": 25,  # Durchschnittsalter
            "club": club,
            "value": "$1.000",  # Minimaler Wert
            # Alle Fußball-Attribute auf niedrigem Level
            "ball_control": 30,
            "dribbling": 30,
            "slide_tackle": 30,
            "stand_tackle": 30,
            "aggression": 30,
            "reactions": 30,
            "att_position": 30,
            "interceptions": 30,
            "vision": 30,
            "composure": 30,
            "crossing": 30,
            "short_pass": 30,
            "long_pass": 30,
            "acceleration": 30,
            "stamina": 30,
            "strength": 30,
            "balance": 30,
            "sprint_speed": 30,
            "agility": 30,
            "jumping": 30,
            "heading": 30,
            "shot_power": 30,
            "finishing": 30,
            "long_shots": 30,
        }
        
        return Player(name, dummy_data)
    
    @staticmethod
    def _print_final_squad_info(
        buyer_name: str, buyer_players: List[Player],
        seller_name: str, seller_players: List[Player]
    ):
        """
        Zeigt finale Informationen über die Club-Squads
        """
        if not DISPLAY_CONFIG.get("SHOW_INITIAL_SQUADS", True):
            return
        
        print(f"\n✅ FINALE SQUAD-ZUSAMMENSETZUNG:")
        print("-" * 50)
        print(f"{buyer_name}: {len(buyer_players)} Spieler")
        print(f"{seller_name}: {len(seller_players)} Spieler")
        
        # Prüfe auf Dummy-Spieler
        buyer_dummies = sum(1 for p in buyer_players if "Reserve Player" in p.name)
        seller_dummies = sum(1 for p in seller_players if "Reserve Player" in p.name)
        
        if buyer_dummies > 0:
            print(f"  {buyer_name}: {buyer_dummies} Dummy-Spieler")
        if seller_dummies > 0:
            print(f"  {seller_name}: {seller_dummies} Dummy-Spieler")
        
        print("-" * 50)
    
    @staticmethod
    def _clean_row(row: Dict[str, str]) -> Dict[str, str]:
        """
        Bereinigt eine Datenzeile und ersetzt leere Werte
        
        Args:
            row: Rohe CSV-Zeile als Dictionary
            
        Returns:
            Dict[str, str]: Bereinigte Datenzeile
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
    def _create_sample_clubs(
        buyer_club_name: str, 
        seller_club_name: str
    ) -> Tuple[List[Player], List[Player]]:
        """
        Erstellt Beispiel-Squads für beide Clubs falls CSV nicht verfügbar
        
        Args:
            buyer_club_name: Name des Käufer-Clubs
            seller_club_name: Name des Verkäufer-Clubs
            
        Returns:
            Tuple[List[Player], List[Player]]: Beispiel-Squads
        """
        print(f"\n🔄 ERSTELLE BEISPIEL-SQUADS:")
        print(f"Käufer: {buyer_club_name}")
        print(f"Verkäufer: {seller_club_name}")
        
        squad_size = CLUB_CONFIG.get("MIN_PLAYERS_REQUIRED", 11)
        
        buyer_players = ClubBasedPlayerDataLoader._create_sample_squad(
            buyer_club_name, squad_size
        )
        seller_players = ClubBasedPlayerDataLoader._create_sample_squad(
            seller_club_name, squad_size
        )
        
        print(f"✅ Erstellt: {len(buyer_players)} Spieler pro Club")
        
        return buyer_players, seller_players
    
    @staticmethod
    def _create_sample_squad(club_name: str, squad_size: int) -> List[Player]:
        """
        Erstellt einen Beispiel-Squad für einen Club
        
        Args:
            club_name: Name des Clubs
            squad_size: Anzahl Spieler im Squad
            
        Returns:
            List[Player]: Beispiel-Squad
        """
        import random
        
        # Sample Namen für verschiedene Nationalitäten
        sample_names = [
            ("João Silva", "Brazil"),
            ("Marco Rossi", "Italy"), 
            ("Hans Mueller", "Germany"),
            ("Pierre Dupont", "France"),
            ("David Smith", "England"),
            ("Carlos Rodriguez", "Spain"),
            ("Ahmed Hassan", "Egypt"),
            ("Hiroshi Tanaka", "Japan"),
            ("Lars Andersen", "Denmark"),
            ("Piotr Kowalski", "Poland"),
        ]
        
        players = []
        
        for i in range(squad_size):
            # Wähle zufälligen Namen und Nation
            name_template, country = random.choice(sample_names)
            name = f"{name_template} {i+1}"
            
            # Erstelle realistische Attribute
            data = {
                "country": country,
                "age": random.randint(18, 35),
                "club": club_name,
                "value": f"${random.randint(100, 5000)}.000",
                # Realistische Attribut-Verteilungen
                "ball_control": random.randint(40, 90),
                "dribbling": random.randint(30, 85),
                "slide_tackle": random.randint(25, 80),
                "stand_tackle": random.randint(30, 85),
                "aggression": random.randint(35, 90),
                "reactions": random.randint(45, 90),
                "att_position": random.randint(25, 85),
                "interceptions": random.randint(30, 85),
                "vision": random.randint(35, 90),
                "composure": random.randint(40, 85),
                "crossing": random.randint(25, 80),
                "short_pass": random.randint(45, 90),
                "long_pass": random.randint(30, 85),
                "acceleration": random.randint(40, 90),
                "stamina": random.randint(55, 95),
                "strength": random.randint(45, 90),
                "balance": random.randint(50, 85),
                "sprint_speed": random.randint(40, 90),
                "agility": random.randint(45, 85),
                "jumping": random.randint(35, 80),
                "heading": random.randint(30, 80),
                "shot_power": random.randint(25, 85),
                "finishing": random.randint(20, 85),
                "long_shots": random.randint(25, 80),
            }
            
            player = Player(name, data)
            players.append(player)
        
        return players

    # Rückwärts-Kompatibilität für das alte System
    @staticmethod
    def load_from_csv(file_path: str = None, max_players: int = None) -> List[Player]:
        """
        DEPRECATED: Alte Methode für Rückwärts-Kompatibilität
        Verwende stattdessen load_clubs_from_csv()
        """
        print("⚠️ Warnung: load_from_csv() ist deprecated!")
        print("   Verwende load_clubs_from_csv() für Club-basierte Auswahl")
        
        # Lade einfach die ersten max_players aus der CSV
        if file_path is None:
            file_path = SYSTEM_CONFIG["CSV_FILE_PATH"]
        if max_players is None:
            max_players = 30
        
        all_players = ClubBasedPlayerDataLoader._load_all_players_from_csv(file_path)
        return all_players[:max_players]