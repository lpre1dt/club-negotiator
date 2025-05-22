import random
from typing import List, Tuple, Optional
# Import Player class
from PlayerAgent import Player


class ClubBasedFootballMediator:
    """
    Vermittler (Mediator) für club-basierte Fußballspieler-Verhandlungen.

    Diese Klasse ist zentral für die Koordination von Verhandlungsvorschlägen zwischen
    zwei Fußball-Clubs (Agenten). Sie unterstützt Verhandlungen mit unterschiedlich
    großen Spielerkadern und bietet Mechanismen für verschiedene Arten von
    Tauschangeboten:
    - Interne Positionswechsel innerhalb eines Teams (`propose_player_swap`, `propose_team_shuffle`).
    - Direkte Spielertausche zwischen den beiden Clubs (`propose_inter_club_swap`).

    Der Mediator speichert die Spielerpools beider Clubs und protokolliert alle
    Tauschentscheidungen (`trade_log`). Er validiert auch die Konsistenz
    der Kader (repräsentiert durch Indexlisten für positionsbasierte Agenten).

    Wichtige Merkmale:
    - Initialisierung mit den Spielerlisten (Pools) beider Clubs.
    - Generierung von initialen Kaderaufstellungen (als Indexlisten).
    - Vorschlag von verschiedenen Tauschtypen.
    - Protokollierung von Tauschangeboten und deren Ergebnissen.
    - Validierung von Kaderzuständen.
    """

    def __init__(self, buyer_players_pool: List[Player], seller_players_pool: List[Player]):
        """
        Initialisiert den `ClubBasedFootballMediator`.

        Args:
            buyer_players_pool (List[Player]): Eine Liste von `Player`-Objekten, die den
                                               Spielerpool des Käufer-Clubs repräsentiert.
            seller_players_pool (List[Player]): Eine Liste von `Player`-Objekten, die den
                                                Spielerpool des Verkäufer-Clubs repräsentiert.
        """
        # Speichert die übergebenen Spielerlisten als Pools für Käufer und Verkäufer.
        self.buyer_players_pool: List[Player] = buyer_players_pool
        self.seller_players_pool: List[Player] = seller_players_pool
        
        # Ermittle die Größe der Spielerpools für Käufer und Verkäufer.
        self.buyer_size: int = len(self.buyer_players_pool)
        self.seller_size: int = len(self.seller_players_pool)
        
        # Hilfsvariablen für minimale und maximale Kadergröße, nützlich für bestimmte Strategien.
        self.min_size: int = min(self.buyer_size, self.seller_size)
        self.max_size: int = max(self.buyer_size, self.seller_size)

        self.trade_log: list = [] # Initialisiert das Protokoll für Tauschentscheidungen.
        
        print(f"🏟️ MEDIATOR INITIALISIERT:")
        print(f"   Käufer-Pool Größe: {self.buyer_size} Spieler") # Korrigierte Ausgabebezeichnung
        print(f"   Verkäufer-Pool Größe: {self.seller_size} Spieler") # Korrigierte Ausgabebezeichnung
        
        # Anmerkung: Die `buyer_size` und `seller_size` Attribute beziehen sich auf die Größe
        # der übergebenen Spieler-Pools. Die `init_squads` Methode erstellt basierend darauf
        # Listen von Indices, die die initiale Anordnung der Spieler für positionsbasierte
        # Utility-Berechnungen darstellen.

    def init_squads(self) -> Tuple[List[int], List[int]]:
        """
        Erstellt die initialen Kaderaufstellungen für beide Clubs als Listen von Positions-Indices.

        Diese Indexlisten repräsentieren die anfängliche Anordnung der Spieler aus den
        entsprechenden Spielerpools (`self.buyer_players_pool`, `self.seller_players_pool`).
        Jeder Index entspricht einem Spieler im jeweiligen Pool.
        
        Returns:
            Tuple[List[int], List[int]]: Ein Tupel bestehend aus zwei Listen:
                                           - `buyer_squad_indices`: Liste der Indices für den Käufer-Kader.
                                           - `seller_squad_indices`: Liste der Indices für den Verkäufer-Kader.
                                           Beide Listen sind initial sequenziell von 0 bis `size-1`.
        """
        # Erzeuge eine sequenzielle Liste von Indices für jeden Kader.
        buyer_squad_indices = list(range(self.buyer_size))
        seller_squad_indices = list(range(self.seller_size))
        
        print(f"\n📋 INITIALE POSITIONS-SQUADS (INDICES) ERSTELLT:")
        print(f"   Käufer-Squad-Indices: {buyer_squad_indices}")
        print(f"   Verkäufer-Squad-Indices: {seller_squad_indices}")
        
        return buyer_squad_indices, seller_squad_indices

    def propose_player_swap(
        self, 
        buyer_squad: List[int], 
        seller_squad: List[int]
    ) -> Tuple[List[int], List[int]]:
        """
        Schlägt einen *intra-team* Positions-Tausch innerhalb der Squads vor.

        Dieser Tausch betrifft die Anordnung von Spielern (repräsentiert durch Indices)
        INNERHALB eines einzelnen Clubs und ist NICHT für Tausche zwischen Clubs.
        Die Spieler-Objekte selbst werden hier nicht bewegt, nur ihre Positionen.
        
        Args:
            buyer_squad: Aktuelle Käufer-Squad-Aufstellung (Liste von Indices).
            seller_squad: Aktuelle Verkäufer-Squad-Aufstellung (Liste von Indices).
            
        Returns:
            Tuple[List[int], List[int]]: Neue Squad-Aufstellungen nach dem internen Swap.
        """
        # Wähle zufällig einen der beiden Squads für den Swap
        if random.choice([True, False]) and self.buyer_size > 1:
            # Swap im Käufer-Squad
            new_buyer_squad = self._swap_positions_in_squad(buyer_squad)
            new_seller_squad = seller_squad.copy()
        elif self.seller_size > 1:
            # Swap im Verkäufer-Squad
            new_buyer_squad = buyer_squad.copy()
            new_seller_squad = self._swap_positions_in_squad(seller_squad)
        else:
            # Fallback: Keine Änderung, wenn beide Squads zu klein sind
            new_buyer_squad = buyer_squad.copy()
            new_seller_squad = seller_squad.copy()
        
        return new_buyer_squad, new_seller_squad

    def _swap_positions_in_squad(self, squad: List[int]) -> List[int]:
        """
        Tauscht zwei zufällige Positionen (Indices) innerhalb eines Squads.
        Dies ist eine Hilfsmethode für *intra-team* Swaps.
        
        Args:
            squad: Squad-Aufstellung (Liste von Indices).
            
        Returns:
            List[int]: Squad mit getauschten Positionen (Indices).
        """
        squad_len = len(squad)
        if squad_len <= 1:
            return squad.copy()
        
        new_squad = squad.copy()
        
        # Wähle zwei verschiedene Positionen
        pos1 = random.randrange(squad_len)
        pos2 = random.randrange(squad_len)
        
        # Sicherstellen, dass verschiedene Positionen gewählt werden
        while pos1 == pos2: # Loop only needed if squad_len > 1, which is already checked
            pos2 = random.randrange(squad_len)
        
        # Tausche die Indices an diesen Positionen
        new_squad[pos1], new_squad[pos2] = new_squad[pos2], new_squad[pos1]
        
        return new_squad

    def propose_team_shuffle(
        self, 
        buyer_squad: List[int], 
        seller_squad: List[int],
        shuffle_percentage: float = 0.3
    ) -> Tuple[List[int], List[int]]:
        """
        Schlägt eine größere *intra-team* Positions-Umstellung in einem oder beiden Teams vor.
        
        Dieser Shuffle betrifft die Anordnung von Spielern (repräsentiert durch Indices)
        INNERHALB eines einzelnen Clubs und ist NICHT für Tausche zwischen Clubs.
        Die Spieler-Objekte selbst werden hier nicht bewegt, nur ihre Positionen.

        Args:
            buyer_squad: Aktuelle Käufer-Squad-Aufstellung (Liste von Indices).
            seller_squad: Aktuelle Verkäufer-Squad-Aufstellung (Liste von Indices).
            shuffle_percentage: Anteil der Spielerpositionen, die umgestellt werden sollen.
            
        Returns:
            Tuple[List[int], List[int]]: Neue Squad-Aufstellungen nach dem internen Shuffle.
        """
        # Entscheide zufällig welche Squads geshuffelt werden
        shuffle_buyer = random.choice([True, False]) if self.buyer_size > 1 else False
        shuffle_seller = random.choice([True, False]) if self.seller_size > 1 else False
        
        # Mindestens einer muss geshuffelt werden, wenn möglich
        if not shuffle_buyer and not shuffle_seller:
            if self.buyer_size > 1: shuffle_buyer = True
            elif self.seller_size > 1: shuffle_seller = True
            # If both are size 1 or less, no shuffle happens.
        
        new_buyer_squad = buyer_squad.copy()
        new_seller_squad = seller_squad.copy()
        
        if shuffle_buyer:
            new_buyer_squad = self._shuffle_squad(new_buyer_squad, shuffle_percentage)
        
        if shuffle_seller:
            new_seller_squad = self._shuffle_squad(new_seller_squad, shuffle_percentage)
        
        return new_buyer_squad, new_seller_squad

    def _shuffle_squad(self, squad: List[int], percentage: float) -> List[int]:
        """
        Shuffelt einen Anteil der Positionen (Indices) in einem Squad.
        Dies ist eine Hilfsmethode für *intra-team* Shuffles.
        
        Args:
            squad: Zu shuffelnde Squad-Aufstellung (Liste von Indices).
            percentage: Anteil der zu shufflenden Positionen (0.0 bis 1.0).
            
        Returns:
            List[int]: Squad mit geshuffelten Positionen (Indices).
        """
        squad_len = len(squad)
        if squad_len <= 1:
            return squad.copy()
        
        new_squad = squad.copy()
        num_to_shuffle = max(1, int(squad_len * percentage))
        # Ensure num_to_shuffle is not greater than squad_len, can happen if percentage > 1 by mistake
        num_to_shuffle = min(num_to_shuffle, squad_len)
        
        
        # Wähle zufällige Positionen zum Shuffeln
        positions_to_shuffle = random.sample(range(squad_len), num_to_shuffle)
        
        # Extrahiere die Indices an diesen Positionen
        indices_at_positions = [new_squad[i] for i in positions_to_shuffle]
        
        # Shuffele diese Indices
        random.shuffle(indices_at_positions)
        
        # Setze die geshuffelten Indices zurück an die ausgewählten Positionen
        for i, original_index_val in enumerate(positions_to_shuffle):
            new_squad[original_index_val] = indices_at_positions[i]
        
        return new_squad

    def propose_inter_club_swap(self) -> Tuple[Optional[Player], Optional[Player]]:
        """
        Schlägt einen Tausch von einem Spieler des Käufers gegen einen Spieler des Verkäufers vor.

        Returns:
            Tuple[Optional[Player], Optional[Player]]: 
                (ausgewählter Käufer-Spieler, ausgewählter Verkäufer-Spieler).
                Gibt (None, None) zurück, wenn einer der Spieler-Pools leer ist.
        """
        if not self.buyer_players_pool or not self.seller_players_pool:
            print("⚠️ Warnung: Inter-Club Swap nicht möglich, einer der Spieler-Pools ist leer.")
            return None, None

        selected_buyer_player = random.choice(self.buyer_players_pool)
        selected_seller_player = random.choice(self.seller_players_pool)
        
        return selected_buyer_player, selected_seller_player

    def record_trade_decision(
        self, 
        buyer_player_offered: Optional[Player], 
        seller_player_offered: Optional[Player], 
        buyer_accepted: bool, 
        seller_accepted: bool, 
        trade_executed: bool
    ):
        """
        Protokolliert die Details und das Ergebnis eines Inter-Club-Tauschangebots.

        Args:
            buyer_player_offered: Der Spieler-Objekt, das der Käufer angeboten hat (None wenn kein Angebot).
            seller_player_offered: Der Spieler-Objekt, das der Verkäufer angeboten hat (None wenn kein Angebot).
            buyer_accepted: Boolean, ob der Käufer den vorgeschlagenen Tausch akzeptiert hat.
            seller_accepted: Boolean, ob der Verkäufer den vorgeschlagenen Tausch akzeptiert hat.
            trade_executed: Boolean, ob der Tausch basierend auf den Akzeptanzen durchgeführt wurde.
        """
        log_entry = {
            "buyer_player_offered_name": buyer_player_offered.name if buyer_player_offered else "N/A",
            "seller_player_offered_name": seller_player_offered.name if seller_player_offered else "N/A",
            "buyer_accepted": buyer_accepted,
            "seller_accepted": seller_accepted,
            "trade_executed": trade_executed,
            # buyer_player_received would be seller_player_offered,
            # seller_player_received would be buyer_player_offered.
            # Storing offered players is sufficient to understand the exchange.
        }
        self.trade_log.append(log_entry)
        # Optional: print(f"Trade Logged: {log_entry}")


    def validate_squads(
        self, 
        buyer_squad: List[int], 
        seller_squad: List[int]
    ) -> Tuple[bool, str]:
        """
        Validiert ob die Squad-Aufstellungen (Listen von Indices) gültig sind.
        
        Args:
            buyer_squad: Käufer-Squad-Aufstellung (Liste von Indices).
            seller_squad: Verkäufer-Squad-Aufstellung (Liste von Indices).
            
        Returns:
            Tuple[bool, str]: (Ist gültig?, Fehlermeldung falls ungültig)
        """
        # Prüfe Käufer-Squad
        if len(buyer_squad) != self.buyer_size:
            return False, f"Käufer-Squad hat falsche Größe: {len(buyer_squad)} statt {self.buyer_size}"
        
        # Prüfe ob alle Indices im gültigen Bereich sind
        if not all(0 <= idx < self.buyer_size for idx in buyer_squad):
            return False, f"Käufer-Squad enthält ungültige Indices"
        
        # Prüfe auf Duplikate
        if len(set(buyer_squad)) != len(buyer_squad):
            return False, f"Käufer-Squad enthält Duplikate"
        
        # Prüfe Verkäufer-Squad
        if len(seller_squad) != self.seller_size:
            return False, f"Verkäufer-Squad hat falsche Größe: {len(seller_squad)} statt {self.seller_size}"
        
        # Prüfe ob alle Indices im gültigen Bereich sind
        if not all(0 <= idx < self.seller_size for idx in seller_squad):
            return False, f"Verkäufer-Squad enthält ungültige Indices"
        
        # Prüfe auf Duplikate
        if len(set(seller_squad)) != len(seller_squad):
            return False, f"Verkäufer-Squad enthält Duplikate"
        
        return True, "Squads sind gültig"

    def get_negotiation_statistics(self) -> dict:
        """
        Gibt Statistiken über die Verhandlungs-Parameter zurück
        
        Returns:
            dict: Mediator-Statistiken
        """
        return {
            "buyer_squad_size": self.buyer_size, # Should reflect actual pool size for player objects
            "seller_squad_size": self.seller_size, # Should reflect actual pool size for player objects
            "min_squad_size": self.min_size, # Based on pool sizes
            "max_squad_size": self.max_size, # Based on pool sizes
            "squads_equal_size": self.buyer_size == self.seller_size,
            "size_difference": abs(self.buyer_size - self.seller_size),
            "trade_log_entries": len(self.trade_log) # New statistic
        }


# Rückwärts-Kompatibilität: Alias für alten Mediator
class FootballMediator(ClubBasedFootballMediator):
    """
    Alias für Rückwärts-Kompatibilität mit dem alten System.
    
    DEPRECATED: Verwende ClubBasedFootballMediator direkt.
    Dieser Alias ist möglicherweise nicht voll funktionsfähig mit neuen Features
    wie Inter-Club-Swaps ohne Anpassung der aufrufenden Logik.
    """
    def __init__(self, num_players_a: int, num_players_b: int):
        print("⚠️ Warnung: FootballMediator ist deprecated!")
        print("   Verwende ClubBasedFootballMediator für vollständige Funktionalität")
        # Erstelle Dummy-Spieler-Pools für den neuen Konstruktor
        dummy_buyer_pool = [Player(f"BuyerSamplePlayer{i+1}", {}) for i in range(num_players_a)]
        dummy_seller_pool = [Player(f"SellerSamplePlayer{i+1}", {}) for i in range(num_players_b)]
        super().__init__(dummy_buyer_pool, dummy_seller_pool)
    
    def init_squads(self) -> List[int]:
        """
        DEPRECATED: Alte Methode für Kompatibilität
        Gibt nur den Käufer-Squad zurück
        """
        buyer_squad, seller_squad = super().init_squads()
        print("⚠️ Warnung: init_squads() Rückgabewert geändert!")
        print("   Neue Version gibt Tuple[List[int], List[int]] zurück")
        return buyer_squad
    
    def propose_player_swap(self, current_squad: List[int]) -> List[int]:
        """
        DEPRECATED: Alte Methode für Kompatibilität
        Nimmt nur einen Squad und gibt einen zurück
        """
        # Erstelle dummy seller squad
        seller_squad = list(range(len(current_squad)))
        buyer_squad, _ = super().propose_player_swap(current_squad, seller_squad)
        return buyer_squad
    
    def propose_team_shuffle(
        self, 
        current_squad: List[int], 
        shuffle_percentage: float = 0.3
    ) -> List[int]:
        """
        DEPRECATED: Alte Methode für Kompatibilität
        Nimmt nur einen Squad und gibt einen zurück
        """
        # Erstelle dummy seller squad
        seller_squad = list(range(len(current_squad)))
        buyer_squad, _ = super().propose_team_shuffle(
            current_squad, seller_squad, shuffle_percentage
        )
        return buyer_squad