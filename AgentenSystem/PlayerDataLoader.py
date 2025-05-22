import csv
from typing import List, Dict, Tuple, Optional
from PlayerAgent import Player
from config import SYSTEM_CONFIG, CLUB_CONFIG, DISPLAY_CONFIG


class ClubBasedPlayerDataLoader:
    """
    Verantwortlich für das Laden, Verarbeiten und Validieren von Spielerdaten aus CSV-Dateien.
    Diese Klasse ermöglicht eine Club-basierte Auswahl von Spielern und bietet Mechanismen
    zur Handhabung von unterschiedlich großen Kadern sowie zur Datenbereinigung.

    Hauptfunktionen:
    1. Laden aller Spieler aus einer spezifizierten CSV-Datei.
    2. Filtern der Spieler basierend auf konfigurierten Club-Namen (Käufer und Verkäufer).
    3. Anwenden von Strategien zum Umgang mit unterschiedlichen Kadergrößen (z.B. Auffüllen, Kürzen).
    4. Validierung der geladenen Daten und Kadergrößen anhand definierter Mindestanforderungen.
    5. Bereinigung von Rohdaten aus der CSV, um Konsistenz sicherzustellen.
    6. Erstellung von Beispiel-Kadern, falls die Datenquelle nicht verfügbar ist und dies konfiguriert wurde.

    Alle Operationen werden als statische Methoden implementiert, da die Klasse primär als Utility-Sammlung dient.
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
            buyer_club_name (str, optional): Name des Käufer-Clubs. 
                Standardmäßig aus `CLUB_CONFIG`.
            seller_club_name (str, optional): Name des Verkäufer-Clubs. 
                Standardmäßig aus `CLUB_CONFIG`.
            file_path (str, optional): Pfad zur CSV-Datei. 
                Standardmäßig aus `SYSTEM_CONFIG`.
            
        Returns:
            Tuple[List[Player], List[Player]]: Ein Tupel, das zwei Listen von Spieler-Objekten enthält:
                (Liste der Spieler des Käufer-Clubs, Liste der Spieler des Verkäufer-Clubs).
            
        Raises:
            FileNotFoundError: Wird ausgelöst, wenn die angegebene CSV-Datei nicht gefunden wird und
                `FALLBACK_TO_SAMPLE_DATA` deaktiviert ist.
            ValueError: Wird ausgelöst, wenn ein Club nicht genügend Spieler gemäß 
                `MIN_PLAYERS_REQUIRED` hat und `FALLBACK_TO_SAMPLE_DATA` deaktiviert ist 
                (obwohl die aktuelle Implementierung dies eher durch Logging handhabt und ggf. leere Listen liefert).
        """
        # Lade Konfigurationswerte, falls keine spezifischen Parameter übergeben wurden.
        # Dies ermöglicht Flexibilität beim Aufruf der Methode.
        effective_buyer_club_name = buyer_club_name or CLUB_CONFIG["BUYER_CLUB_NAME"]
        effective_seller_club_name = seller_club_name or CLUB_CONFIG["SELLER_CLUB_NAME"]
        effective_file_path = file_path or SYSTEM_CONFIG["CSV_FILE_PATH"]
        
        print("=" * 70)
        print("CLUB-BASIERTE SPIELER-AUSWAHL")
        print("=" * 70)
        print(f"CSV Datei: {effective_file_path}")
        print(f"Käufer Club: {effective_buyer_club_name}")
        print(f"Verkäufer Club: {effective_seller_club_name}")
        print()
        
        try:
            # Schritt 1: Lade alle Spieler aus der CSV-Datei.
            all_players = ClubBasedPlayerDataLoader._load_all_players_from_csv(effective_file_path)
            
            # Schritt 2: Filtere Spieler basierend auf den Club-Namen.
            buyer_players = ClubBasedPlayerDataLoader._filter_players_by_club(
                all_players, effective_buyer_club_name
            )
            seller_players = ClubBasedPlayerDataLoader._filter_players_by_club(
                all_players, effective_seller_club_name
            )
            
            # Schritt 3: Zeige grundlegende Statistiken für die gefundenen Spieler.
            ClubBasedPlayerDataLoader._print_club_statistics(
                effective_buyer_club_name, buyer_players, 
                effective_seller_club_name, seller_players
            )
            
            # Schritt 4: Validiere die Kadergrößen gegen die Mindestanforderungen.
            # Diese Methode könnte eine Exception auslösen, wenn FALLBACK_TO_SAMPLE_DATA False ist.
            ClubBasedPlayerDataLoader._validate_squad_sizes(
                effective_buyer_club_name, buyer_players, 
                effective_seller_club_name, seller_players
            )
            
            # Schritt 5: Behandle Unterschiede in den Kadergrößen gemäß der konfigurierten Strategie.
            buyer_players, seller_players = ClubBasedPlayerDataLoader._handle_squad_size_differences(
                effective_buyer_club_name, buyer_players, 
                effective_seller_club_name, seller_players
            )
            
            # Schritt 6: Zeige finale Informationen zu den aufbereiteten Kadern.
            ClubBasedPlayerDataLoader._print_final_squad_info(
                effective_buyer_club_name, buyer_players, 
                effective_seller_club_name, seller_players
            )
            
            return buyer_players, seller_players
            
        except FileNotFoundError:
            # Fehlerbehandlung, falls die CSV-Datei nicht gefunden wird.
            print(f"❌ Fehler: CSV-Datei nicht gefunden unter: {effective_file_path}")
            
            # Optionale Erstellung von Beispieldaten als Fallback.
            if CLUB_CONFIG.get("FALLBACK_TO_SAMPLE_DATA", True):
                print("🔄 Erstelle Beispieldaten für beide Clubs als Fallback...")
                return ClubBasedPlayerDataLoader._create_sample_clubs(
                    effective_buyer_club_name, effective_seller_club_name
                )
            else:
                # Wenn kein Fallback erwünscht ist, wird die Exception weitergereicht.
                raise
    
    @staticmethod
    def _load_all_players_from_csv(file_path: str) -> List[Player]:
        """
        Lädt alle Spieler aus der CSV-Datei
        
        Args:
            file_path (str): Der Pfad zur CSV-Datei, die die Spielerdaten enthält.
            
        Returns:
            List[Player]: Eine Liste von `Player`-Objekten, die aus der CSV-Datei erstellt wurden.
                          Gibt eine leere Liste zurück, wenn die Datei nicht gelesen werden kann oder leer ist.
        
        Hinweis:
            Verwendet die in `SYSTEM_CONFIG` definierte Zeichenkodierung und das Trennzeichen ';'.
            Fehlerhafte Zeilen werden übersprungen und eine Warnung wird ausgegeben.
        """
        players = [] # Initialisiere eine leere Liste für die Spielerobjekte.
        # Hole die konfigurierte Zeichenkodierung; Standard ist "utf-8".
        encoding = SYSTEM_CONFIG.get("CSV_ENCODING", "utf-8")
        
        print(f"🔄 Lade alle Spieler aus CSV-Datei: {file_path} (Encoding: {encoding})...")
        
        try:
            with open(file_path, "r", encoding=encoding) as file:
                # Verwende csv.DictReader für einfachen Zugriff auf Spalten per Namen.
                # Das Trennzeichen ist ';' wie in der Datei verwendet.
                reader = csv.DictReader(file, delimiter=';')
                
                for row_num, row_data_dict in enumerate(reader, 1):
                    try:
                        # Bereinige die eingelesenen Rohdaten der Zeile.
                        cleaned_row = ClubBasedPlayerDataLoader._clean_row(row_data_dict)
                        
                        # Erstelle ein Player-Objekt aus den bereinigten Daten.
                        # Die 'player'-Spalte wird für den Namen des Spielers verwendet.
                        player_name = cleaned_row.get("player", f"Unbekannter Spieler Zeile {row_num}")
                        player = Player(player_name, cleaned_row)
                        players.append(player)
                        
                    except KeyError as ke:
                        # Spezifische Fehlermeldung für fehlende, aber erwartete Schlüssel.
                        print(f"⚠️ Warnung: Fehlender Schlüssel '{ke}' in Zeile {row_num}. Überspringe Zeile.")
                        continue
                    except Exception as e:
                        # Allgemeine Fehlermeldung für andere Probleme beim Verarbeiten einer Zeile.
                        print(f"⚠️ Warnung: Fehler beim Verarbeiten von Zeile {row_num}: {e}. Überspringe Zeile.")
                        continue
            
            print(f"✅ {len(players)} Spieler erfolgreich aus CSV geladen.")
        except Exception as e:
            # Fehlerbehandlung für Probleme beim Öffnen oder Lesen der Datei.
            print(f"❌ Kritischer Fehler beim Laden aller Spieler aus CSV: {e}")
            # In diesem Fall wird eine leere Spielerliste zurückgegeben.
            
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
        # Standard exact match
        exact_matches = [p for p in players if p.club == club_name]
        if exact_matches:
            return exact_matches

        # Specific fallback for "FC Bayern München" due to known encoding issues in CSV
        # \xfc is the latin-1 encoding for ü
        if club_name == "FC Bayern München":
            # Try common variations seen in data that might result from latin1 decode
            potential_matches = ["FC Bayern M\xfcnchen", "FC Bayern Mðnchen"] 
            for potential_match in potential_matches:
                fallback_matches = [p for p in players if p.club == potential_match]
                if fallback_matches:
                    print(f"ℹ️ Info: Club '{club_name}' nicht exakt gefunden, aber Übereinstimmung mit '{potential_match}' durch Fallback.")
                    return fallback_matches
        
        # Generic fallback: case-insensitive and partial match
        print(f"⚠️ Warnung: Keine exakte Übereinstimmung für '{club_name}'. Suche nach ähnlichen Club-Namen...")
        
        # Simplified similar match: case-insensitive exact or substring
        # This is less complex than full normalization if the above specific fallbacks handle the main problem.
        club_name_lower = club_name.lower()
        similar_matches = [
            p for p in players 
            if club_name_lower == p.club.lower() # case-insensitive exact
        ]
        if similar_matches:
             print(f"   Gefunden durch case-insensitive exakte Übereinstimmung: '{similar_matches[0].club}'")
             return similar_matches

        similar_matches_partial = [
            p for p in players
            if club_name_lower in p.club.lower() or p.club.lower() in club_name_lower
        ]

        if similar_matches_partial:
            # Prefer matches where the found club name is shorter or equal, or starts with the query
            # This tries to avoid overly broad matches like "FC" matching "FC Porto", "FC Barcelona", etc.
            # when just "FC" was (mistakenly) searched.
            # A simple heuristic: pick the one with the smallest length difference, or where query is substring
            
            best_match_club_name = None
            min_len_diff = float('inf')

            grouped_by_found_club = {}
            for p in similar_matches_partial:
                if p.club not in grouped_by_found_club:
                    grouped_by_found_club[p.club] = []
                grouped_by_found_club[p.club].append(p)

            if grouped_by_found_club:
                # Select the most common partially matched club name
                # Or the first one if counts are equal
                # This is a simple heuristic
                sorted_found_clubs = sorted(grouped_by_found_club.keys(), key=lambda c: len(grouped_by_found_club[c]), reverse=True)
                best_match_club_name = sorted_found_clubs[0]

                print(f"   Gefundene ähnliche Clubs (Teilübereinstimmung): {list(grouped_by_found_club.keys())}")
                print(f"   Verwende Spieler vom ähnlichsten Club: '{best_match_club_name}' basierend auf Teilübereinstimmung mit '{club_name}'.")
                return grouped_by_found_club[best_match_club_name]
        
        # Last resort: show available clubs if no good match found
        available_clubs = sorted(list(set(p.club for p in players)))
        print(f"❌ Club '{club_name}' auch nach ähnlicher Suche nicht eindeutig gefunden.")
        print(f"   Verfügbare Clubs (erste 20): {available_clubs[:20]}...")
        
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
        cleaned = {}
        default_unknown_keys = ["player", "country", "club"]

        for key, value in row.items():
            clean_key = key.strip() if isinstance(key, str) else (str(key) if key is not None else "UnknownKey")

            if isinstance(value, str):
                clean_value = value.strip()
            elif value is None:
                clean_value = "" 
            else:
                try:
                    clean_value = str(value).strip()
                except:
                    clean_value = "" 

            if not clean_value or clean_value.lower() == "nan":
                if clean_key in default_unknown_keys:
                    clean_value = "Unknown"
                else:
                    clean_value = "0" 
            
            cleaned[clean_key] = clean_value
        
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