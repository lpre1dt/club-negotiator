# TransferTracker.py - Tracking von Spielertransfers während Verhandlungen
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from PlayerAgent import Player


class TransferTracker:
    """
    Verfolgt alle Transfers während einer Verhandlung zwischen zwei Vereinen
    """
    
    def __init__(self, club1_name: str, club2_name: str, all_players: List[Player]):
        """
        Args:
            club1_name: Name des ersten Vereins
            club2_name: Name des zweiten Vereins
            all_players: Liste aller Spieler im Spielerpool
        """
        self.club1_name = club1_name
        self.club2_name = club2_name
        self.all_players = all_players
        
        # Transfer-Historie
        self.transfer_history = []
        self.transfer_count = 0
        
        # Spieler-Tracking
        self.initial_club1_players = set()
        self.initial_club2_players = set()
        self.current_club1_players = set()
        self.current_club2_players = set()
        
    def initialize_squads(self, initial_squad: List[int], squad1_size: int):
        """
        Initialisiert die Startaufstellungen beider Vereine
        
        Args:
            initial_squad: Initiale Squad-Indices
            squad1_size: Größe des ersten Vereins
        """
        # Speichere initiale Spieler-Zuordnungen
        for i in range(squad1_size):
            player_idx = initial_squad[i]
            self.initial_club1_players.add(player_idx)
            self.current_club1_players.add(player_idx)
            
        for i in range(squad1_size, len(initial_squad)):
            player_idx = initial_squad[i]
            self.initial_club2_players.add(player_idx)
            self.current_club2_players.add(player_idx)
            
    def track_transfer(self, old_squad: List[int], new_squad: List[int], 
                      squad1_size: int, round_num: int) -> Optional[Dict]:
        """
        Verfolgt einen Transfer zwischen den Squads
        
        Args:
            old_squad: Alter Squad
            new_squad: Neuer Squad
            squad1_size: Größe des ersten Vereins
            round_num: Aktuelle Runde
            
        Returns:
            Dict mit Transfer-Details oder None wenn kein Transfer
        """
        # Finde Änderungen
        transfers = []
        
        # Prüfe Verein 1
        new_club1 = set(new_squad[:squad1_size])
        old_club1 = set(old_squad[:squad1_size])
        
        # Spieler die Verein 1 verlassen haben
        left_club1 = old_club1 - new_club1
        # Spieler die zu Verein 1 gekommen sind
        joined_club1 = new_club1 - old_club1
        
        if left_club1 and joined_club1:
            # Es gab einen Tausch
            for player_out_idx in left_club1:
                for player_in_idx in joined_club1:
                    # Verifiziere dass es ein echter Tausch ist
                    if player_out_idx in set(new_squad[squad1_size:]) and \
                       player_in_idx in old_club1:
                        continue  # Das ist kein gültiger Tausch
                        
                    player_out = self.all_players[player_out_idx]
                    player_in = self.all_players[player_in_idx]
                    
                    transfer = {
                        'round': round_num,
                        'transfer_num': self.transfer_count + 1,
                        'from_club': self.club1_name,
                        'to_club': self.club2_name,
                        'player_out': {
                            'idx': player_out_idx,
                            'name': player_out.name,
                            'age': player_out.age,
                            'value': player_out.value,
                            'original_club': player_out.club
                        },
                        'player_in': {
                            'idx': player_in_idx,
                            'name': player_in.name,
                            'age': player_in.age,
                            'value': player_in.value,
                            'original_club': player_in.club
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.transfer_history.append(transfer)
                    self.transfer_count += 1
                    
                    # Update current players
                    self.current_club1_players.discard(player_out_idx)
                    self.current_club1_players.add(player_in_idx)
                    self.current_club2_players.discard(player_in_idx)
                    self.current_club2_players.add(player_out_idx)
                    
                    return transfer
                    
        return None
        
    def get_transfer_summary(self) -> Dict:
        """
        Erstellt eine Zusammenfassung aller Transfers
        
        Returns:
            Dict mit Transfer-Zusammenfassung
        """
        # Berechne wer wo gelandet ist
        club1_kept_original = self.current_club1_players & self.initial_club1_players
        club1_got_from_club2 = self.current_club1_players & self.initial_club2_players
        
        club2_kept_original = self.current_club2_players & self.initial_club2_players
        club2_got_from_club1 = self.current_club2_players & self.initial_club1_players
        
        summary = {
            'total_transfers': self.transfer_count,
            'club1': {
                'name': self.club1_name,
                'kept_original': len(club1_kept_original),
                'received_players': len(club1_got_from_club2),
                'original_players': [self.all_players[idx] for idx in sorted(club1_kept_original)],
                'new_players': [self.all_players[idx] for idx in sorted(club1_got_from_club2)]
            },
            'club2': {
                'name': self.club2_name,
                'kept_original': len(club2_kept_original),
                'received_players': len(club2_got_from_club1),
                'original_players': [self.all_players[idx] for idx in sorted(club2_kept_original)],
                'new_players': [self.all_players[idx] for idx in sorted(club2_got_from_club1)]
            },
            'transfer_history': self.transfer_history
        }
        
        return summary
        
    def get_final_squads(self, final_squad: List[int], squad1_size: int) -> Tuple[List[Player], List[Player]]:
        """
        Gibt die finalen Kader beider Vereine zurück
        
        Args:
            final_squad: Finale Squad-Indices
            squad1_size: Größe des ersten Vereins
            
        Returns:
            Tuple mit den finalen Kadern beider Vereine
        """
        club1_final = [self.all_players[idx] for idx in final_squad[:squad1_size]]
        club2_final = [self.all_players[idx] for idx in final_squad[squad1_size:]]
        
        return club1_final, club2_final
        
    def get_player_movements(self) -> Dict[str, List[Dict]]:
        """
        Gibt detaillierte Spielerbewegungen zurück
        
        Returns:
            Dict mit Spielerbewegungen gruppiert nach Spieler
        """
        movements = {}
        
        for transfer in self.transfer_history:
            # Bewegung für Spieler der geht
            player_out_name = transfer['player_out']['name']
            if player_out_name not in movements:
                movements[player_out_name] = []
            movements[player_out_name].append({
                'round': transfer['round'],
                'from': transfer['from_club'],
                'to': transfer['to_club'],
                'direction': 'out'
            })
            
            # Bewegung für Spieler der kommt
            player_in_name = transfer['player_in']['name']
            if player_in_name not in movements:
                movements[player_in_name] = []
            movements[player_in_name].append({
                'round': transfer['round'],
                'from': transfer['to_club'],
                'to': transfer['from_club'],
                'direction': 'in'
            })
            
        return movements
        
    def get_transfer_statistics(self) -> Dict:
        """
        Berechnet erweiterte Transfer-Statistiken
        
        Returns:
            Dict mit statistischen Auswertungen
        """
        if not self.transfer_history:
            return {
                'avg_player_age': 0,
                'total_value_moved': 0,
                'avg_value_per_transfer': 0,
                'most_active_round': None,
                'transfers_by_round': {}
            }
            
        # Altersstatistiken
        ages_out = [t['player_out']['age'] for t in self.transfer_history]
        ages_in = [t['player_in']['age'] for t in self.transfer_history]
        avg_age = (sum(ages_out) + sum(ages_in)) / (len(ages_out) + len(ages_in))
        
        # Wertstatistiken
        values_moved = [t['player_out']['value'] + t['player_in']['value'] 
                       for t in self.transfer_history]
        total_value = sum(values_moved)
        avg_value = total_value / len(self.transfer_history) if self.transfer_history else 0
        
        # Transfers pro Runde
        transfers_by_round = {}
        for transfer in self.transfer_history:
            round_num = transfer['round']
            if round_num not in transfers_by_round:
                transfers_by_round[round_num] = 0
            transfers_by_round[round_num] += 1
            
        most_active_round = max(transfers_by_round.items(), 
                               key=lambda x: x[1])[0] if transfers_by_round else None
        
        return {
            'avg_player_age': avg_age,
            'total_value_moved': total_value,
            'avg_value_per_transfer': avg_value,
            'most_active_round': most_active_round,
            'transfers_by_round': transfers_by_round
        }