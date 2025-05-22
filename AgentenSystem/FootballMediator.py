import random
from typing import List, Tuple, Optional


class ClubBasedFootballMediator:
    """
    Mediator für Club-basierte Fußballspieler-Verhandlungen
    
    Dieser neue Mediator kann mit unterschiedlich großen Squads umgehen und
    koordiniert Spieler-Tausch-Vorschläge zwischen echten Club-Teams.
    
    Wichtige Änderungen:
    - Unterstützt unterschiedliche Squad-Größen
    - Separate Squads für Käufer und Verkäufer
    - Validierung für realistische Tausch-Vorschläge
    """

    def __init__(self, buyer_squad_size: int, seller_squad_size: int):
        """
        Initialisiert den Club-basierten Mediator
        
        Args:
            buyer_squad_size: Anzahl Spieler im Käufer-Squad
            seller_squad_size: Anzahl Spieler im Verkäufer-Squad
            
        Hinweis: Die Squad-Größen können unterschiedlich sein!
        """
        self.buyer_size = buyer_squad_size
        self.seller_size = seller_squad_size
        self.min_size = min(buyer_squad_size, seller_squad_size)
        self.max_size = max(buyer_squad_size, seller_squad_size)
        
        print(f"🏟️ MEDIATOR INITIALISIERT:")
        print(f"   Käufer-Squad: {self.buyer_size} Spieler")
        print(f"   Verkäufer-Squad: {self.seller_size} Spieler")
        
        if self.buyer_size != self.seller_size:
            print(f"   ⚠️ Unterschiedliche Squad-Größen detected!")
            print(f"   Verhandlung wird auf {self.min_size} Positionen beschränkt")

    def init_squads(self) -> Tuple[List[int], List[int]]:
        """
        Erstellt die initialen Squad-Aufstellungen für beide Clubs
        
        Returns:
            Tuple[List[int], List[int]]: (Käufer-Squad, Verkäufer-Squad)
            
        Beide Squads beginnen mit sequenzieller Aufstellung: [0,1,2,3,...]
        """
        buyer_squad = list(range(self.buyer_size))
        seller_squad = list(range(self.seller_size))
        
        print(f"\n📋 INITIALE SQUADS ERSTELLT:")
        print(f"   Käufer-Squad: {buyer_squad}")
        print(f"   Verkäufer-Squad: {seller_squad}")
        
        return buyer_squad, seller_squad

    def propose_player_swap(
        self, 
        buyer_squad: List[int], 
        seller_squad: List[int]
    ) -> Tuple[List[int], List[int]]:
        """
        Schlägt einen Spielertausch innerhalb der Squads vor
        
        Da beide Clubs ihre eigenen Spieler haben, werden Positionen
        nur INNERHALB jedes Clubs getauscht, nicht zwischen Clubs.
        
        Args:
            buyer_squad: Aktuelle Käufer-Squad-Aufstellung
            seller_squad: Aktuelle Verkäufer-Squad-Aufstellung
            
        Returns:
            Tuple[List[int], List[int]]: Neue Squad-Aufstellungen nach Swap
        """
        # Wähle zufällig einen der beiden Squads für den Swap
        if random.choice([True, False]) and len(buyer_squad) > 1:
            # Swap im Käufer-Squad
            new_buyer_squad = self._swap_positions_in_squad(buyer_squad)
            new_seller_squad = seller_squad.copy()
        elif len(seller_squad) > 1:
            # Swap im Verkäufer-Squad
            new_buyer_squad = buyer_squad.copy()
            new_seller_squad = self._swap_positions_in_squad(seller_squad)
        else:
            # Fallback: Keine Änderung
            new_buyer_squad = buyer_squad.copy()
            new_seller_squad = seller_squad.copy()
        
        return new_buyer_squad, new_seller_squad

    def _swap_positions_in_squad(self, squad: List[int]) -> List[int]:
        """
        Tauscht zwei zufällige Positionen innerhalb eines Squads
        
        Args:
            squad: Squad-Aufstellung
            
        Returns:
            List[int]: Squad mit getauschten Positionen
        """
        if len(squad) <= 1:
            return squad.copy()
        
        new_squad = squad.copy()
        
        # Wähle zwei verschiedene Positionen
        pos1 = random.randint(0, len(squad) - 1)
        pos2 = random.randint(0, len(squad) - 1)
        
        # Sicherstellen, dass verschiedene Positionen gewählt werden
        while pos1 == pos2 and len(squad) > 1:
            pos2 = random.randint(0, len(squad) - 1)
        
        # Tausche die Spieler an diesen Positionen
        new_squad[pos1], new_squad[pos2] = new_squad[pos2], new_squad[pos1]
        
        return new_squad

    def propose_team_shuffle(
        self, 
        buyer_squad: List[int], 
        seller_squad: List[int],
        shuffle_percentage: float = 0.3
    ) -> Tuple[List[int], List[int]]:
        """
        Schlägt eine größere Umstellung in einem oder beiden Teams vor
        
        Args:
            buyer_squad: Aktuelle Käufer-Squad-Aufstellung
            seller_squad: Aktuelle Verkäufer-Squad-Aufstellung  
            shuffle_percentage: Anteil der Spieler die umgestellt werden
            
        Returns:
            Tuple[List[int], List[int]]: Neue Squad-Aufstellungen nach Shuffle
        """
        # Entscheide zufällig welche Squads geshuffelt werden
        shuffle_buyer = random.choice([True, False])
        shuffle_seller = random.choice([True, False])
        
        # Mindestens einer muss geshuffelt werden
        if not shuffle_buyer and not shuffle_seller:
            shuffle_buyer = True
        
        new_buyer_squad = buyer_squad.copy()
        new_seller_squad = seller_squad.copy()
        
        if shuffle_buyer:
            new_buyer_squad = self._shuffle_squad(buyer_squad, shuffle_percentage)
        
        if shuffle_seller:
            new_seller_squad = self._shuffle_squad(seller_squad, shuffle_percentage)
        
        return new_buyer_squad, new_seller_squad

    def _shuffle_squad(self, squad: List[int], percentage: float) -> List[int]:
        """
        Shuffelt einen Anteil der Positionen in einem Squad
        
        Args:
            squad: Zu shuffelnde Squad-Aufstellung
            percentage: Anteil der zu shufflenden Positionen (0.0 bis 1.0)
            
        Returns:
            List[int]: Squad mit geshuffelten Positionen
        """
        if len(squad) <= 1:
            return squad.copy()
        
        new_squad = squad.copy()
        num_to_shuffle = max(1, int(len(squad) * percentage))
        
        # Wähle zufällige Positionen zum Shuffeln
        positions_to_shuffle = random.sample(range(len(squad)), num_to_shuffle)
        
        # Extrahiere die Werte an diesen Positionen
        values_to_shuffle = [squad[i] for i in positions_to_shuffle]
        
        # Shuffele diese Werte
        random.shuffle(values_to_shuffle)
        
        # Setze die geshuffelten Werte zurück
        for i, val in zip(positions_to_shuffle, values_to_shuffle):
            new_squad[i] = val
        
        return new_squad

    def validate_squads(
        self, 
        buyer_squad: List[int], 
        seller_squad: List[int]
    ) -> Tuple[bool, str]:
        """
        Validiert ob die Squad-Aufstellungen gültig sind
        
        Args:
            buyer_squad: Käufer-Squad-Aufstellung
            seller_squad: Verkäufer-Squad-Aufstellung
            
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
            "buyer_squad_size": self.buyer_size,
            "seller_squad_size": self.seller_size,
            "min_squad_size": self.min_size,
            "max_squad_size": self.max_size,
            "squads_equal_size": self.buyer_size == self.seller_size,
            "size_difference": abs(self.buyer_size - self.seller_size)
        }


# Rückwärts-Kompatibilität: Alias für alten Mediator
class FootballMediator(ClubBasedFootballMediator):
    """
    Alias für Rückwärts-Kompatibilität mit dem alten System
    
    DEPRECATED: Verwende ClubBasedFootballMediator direkt
    """
    def __init__(self, num_players_a: int, num_players_b: int):
        print("⚠️ Warnung: FootballMediator ist deprecated!")
        print("   Verwende ClubBasedFootballMediator für vollständige Funktionalität")
        super().__init__(num_players_a, num_players_b)
    
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