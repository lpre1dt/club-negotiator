# TransferMarket.py - Für realistischere Transfers
import random
from typing import List, Dict, Tuple, Optional
from PlayerAgent import Player
from ClubAgent import ClubAgent


class TransferMarket:
    """
    Simuliert einen realistischeren Transfermarkt mit mehreren Vereinen
    """
    
    def __init__(self, clubs: Dict[str, ClubAgent], min_squad_size: int = 11):
        """
        Args:
            clubs: Dictionary mit Vereinsnamen und ClubAgent-Objekten
            min_squad_size: Minimale Kadergröße pro Verein
        """
        self.clubs = clubs
        self.min_squad_size = min_squad_size
        self.transfer_history = []
        
    def propose_transfer(self, club1_name: str, club2_name: str) -> Optional[Tuple[Player, Player]]:
        """
        Schlägt einen Transfer zwischen zwei Vereinen vor
        
        Returns:
            Tuple[Player, Player] oder None wenn kein Transfer möglich
        """
        if club1_name not in self.clubs or club2_name not in self.clubs:
            return None
            
        club1 = self.clubs[club1_name]
        club2 = self.clubs[club2_name]
        
        # Stelle sicher, dass beide Vereine genug Spieler haben
        if len(club1.players) <= self.min_squad_size or len(club2.players) <= self.min_squad_size:
            return None
            
        # Wähle zufällige Spieler für Tausch
        player1_idx = random.randint(0, len(club1.players) - 1)
        player2_idx = random.randint(0, len(club2.players) - 1)
        
        player1 = club1.players[player1_idx]
        player2 = club2.players[player2_idx]
        
        return (player1, player2)
    
    def execute_transfer(self, club1_name: str, club2_name: str, 
                        player1: Player, player2: Player) -> bool:
        """
        Führt einen Transfer durch wenn beide Vereine zustimmen
        
        Returns:
            bool: True wenn Transfer erfolgreich, False sonst
        """
        if club1_name not in self.clubs or club2_name not in self.clubs:
            return False
            
        club1 = self.clubs[club1_name]
        club2 = self.clubs[club2_name]
        
        # Finde Spieler-Indices
        try:
            player1_idx = club1.players.index(player1)
            player2_idx = club2.players.index(player2)
        except ValueError:
            return False
        
        # Erstelle temporäre Kader für Bewertung
        club1_squad_current = list(range(len(club1.players)))
        club2_squad_current = list(range(len(club2.players)))
        
        # Temporäre Spielerlisten für Simulation
        club1_players_new = club1.players.copy()
        club2_players_new = club2.players.copy()
        
        # Simuliere Tausch
        club1_players_new[player1_idx] = player2
        club2_players_new[player2_idx] = player1
        
        # Bewerte aktuelle Situation
        club1_old_utility = club1.evaluate_squad(club1_squad_current)
        club2_old_utility = club2.evaluate_squad(club2_squad_current)
        
        # Temporär neue Spieler setzen für Bewertung
        old_club1_players = club1.players
        old_club2_players = club2.players
        
        club1.players = club1_players_new
        club2.players = club2_players_new
        
        club1_new_utility = club1.evaluate_squad(club1_squad_current)
        club2_new_utility = club2.evaluate_squad(club2_squad_current)
        
        # Zurücksetzen für Vote
        club1.players = old_club1_players
        club2.players = old_club2_players
        
        # Beide Vereine müssen zustimmen
        # Verwende die vote Methode mit simulierten Squads
        club1_accepts = club1_new_utility >= club1_old_utility or club1.vote(club1_squad_current, club1_squad_current)
        club2_accepts = club2_new_utility >= club2_old_utility or club2.vote(club2_squad_current, club2_squad_current)
        
        if club1_accepts and club2_accepts:
            # Transfer durchführen
            club1.players = club1_players_new
            club2.players = club2_players_new
            
            # Aktualisiere Club-Zugehörigkeit der Spieler
            player1.club = club2_name
            player2.club = club1_name
            
            # Historie aktualisieren
            self.transfer_history.append({
                "from_club": club1_name,
                "to_club": club2_name,
                "player_out": player1.name,
                "player_in": player2.name,
                "timestamp": len(self.transfer_history)
            })
            
            self.transfer_history.append({
                "from_club": club2_name,
                "to_club": club1_name,
                "player_out": player2.name,
                "player_in": player1.name,
                "timestamp": len(self.transfer_history)
            })
            
            return True
            
        return False
    
    def get_transfer_summary(self) -> Dict[str, Dict[str, int]]:
        """Gibt Zusammenfassung der Transfers zurück"""
        summary = {}
        
        # Initialisiere für alle Clubs
        for club_name in self.clubs:
            summary[club_name] = {
                "transfers_in": 0,
                "transfers_out": 0,
                "net_transfers": 0
            }
            
        # Zähle Transfers
        for transfer in self.transfer_history:
            from_club = transfer["from_club"]
            to_club = transfer["to_club"]
            
            if from_club in summary:
                summary[from_club]["transfers_out"] += 1
            if to_club in summary:
                summary[to_club]["transfers_in"] += 1
            
        # Berechne Netto-Transfers
        for club in summary:
            summary[club]["net_transfers"] = (
                summary[club]["transfers_in"] - summary[club]["transfers_out"]
            )
            
        return summary
    
    def get_recent_transfers(self, limit: int = 10) -> List[Dict]:
        """
        Gibt die letzten Transfers zurück
        
        Args:
            limit: Maximale Anzahl an Transfers
            
        Returns:
            Liste der letzten Transfers
        """
        return self.transfer_history[-limit:] if self.transfer_history else []
    
    def get_club_transfers(self, club_name: str) -> List[Dict]:
        """
        Gibt alle Transfers eines bestimmten Vereins zurück
        
        Args:
            club_name: Name des Vereins
            
        Returns:
            Liste aller Transfers des Vereins
        """
        return [
            transfer for transfer in self.transfer_history
            if transfer["from_club"] == club_name or transfer["to_club"] == club_name
        ]
    
    def simulate_transfer_window(self, max_transfers: int = 50, 
                               rounds: int = 1000) -> Dict[str, any]:
        """
        Simuliert ein komplettes Transfer-Fenster
        
        Args:
            max_transfers: Maximale Anzahl an Transfers
            rounds: Maximale Anzahl an Versuchen
            
        Returns:
            Dictionary mit Statistiken
        """
        successful_transfers = 0
        attempted_transfers = 0
        
        club_names = list(self.clubs.keys())
        
        for _ in range(rounds):
            if successful_transfers >= max_transfers:
                break
                
            # Wähle zwei zufällige Vereine
            if len(club_names) < 2:
                break
                
            club1_name = random.choice(club_names)
            remaining_clubs = [c for c in club_names if c != club1_name]
            club2_name = random.choice(remaining_clubs)
            
            # Schlage Transfer vor
            transfer_proposal = self.propose_transfer(club1_name, club2_name)
            
            if transfer_proposal:
                player1, player2 = transfer_proposal
                attempted_transfers += 1
                
                # Versuche Transfer durchzuführen
                if self.execute_transfer(club1_name, club2_name, player1, player2):
                    successful_transfers += 1
                    
        return {
            "successful_transfers": successful_transfers,
            "attempted_transfers": attempted_transfers,
            "success_rate": (successful_transfers / attempted_transfers * 100) 
                          if attempted_transfers > 0 else 0,
            "transfer_summary": self.get_transfer_summary()
        }