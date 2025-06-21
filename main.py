#!/usr/bin/env python3
"""
FUSSBALL-TRANSFERSYSTEM MIT ECHTEN VEREINEN
Hauptprogramm für Kommandozeile
"""

import time
import random
from typing import List, Dict
from config import *
from PlayerDataLoader import PlayerDataLoader
from ClubAgent import ClubAgent
from FootballMediator import FootballMediator
from TransferMarket import TransferMarket


class TransferNegotiationSystem:
    """Hauptklasse für das Transfersystem"""
    
    def __init__(self):
        self.players_by_club = None
        self.clubs = {}
        
    def load_data(self):
        """Lädt Spielerdaten aus CSV"""
        print("=" * 70)
        print("LADE SPIELERDATEN")
        print("=" * 70)
        
        try:
            self.players_by_club = PlayerDataLoader.load_players_by_club()
            print(f"✅ Erfolgreich {len(self.players_by_club)} Vereine geladen")
            
            # Statistiken
            total_players = sum(len(players) for players in self.players_by_club.values())
            print(f"✅ Gesamt {total_players} Spieler")
            
            # Zeige Top 10 Vereine
            print("\nTop 10 Vereine nach Spieleranzahl:")
            club_sizes = [(club, len(players)) for club, players in self.players_by_club.items()]
            club_sizes.sort(key=lambda x: x[1], reverse=True)
            
            for i, (club, size) in enumerate(club_sizes[:10], 1):
                print(f"{i:2d}. {club:<30} - {size:3d} Spieler")
                
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
            raise
            
    def select_clubs(self) -> tuple:
        """Lässt Benutzer zwei Vereine auswählen"""
        eligible_clubs = PlayerDataLoader.get_clubs_with_min_players(
            self.players_by_club,
            SYSTEM_CONFIG["MIN_PLAYERS_PER_CLUB"]
        )
        
        print(f"\n{len(eligible_clubs)} Vereine mit mindestens "
              f"{SYSTEM_CONFIG['MIN_PLAYERS_PER_CLUB']} Spielern verfügbar")
        
        # Automatische Auswahl für Demo
        if len(eligible_clubs) < 2:
            raise ValueError("Nicht genug Vereine für Verhandlung!")
            
        # Wähle zwei zufällige Vereine
        club1 = random.choice(eligible_clubs)
        remaining = [c for c in eligible_clubs if c != club1]
        club2 = random.choice(remaining)
        
        print(f"\nAusgewählte Vereine:")
        print(f"1. {club1} ({len(self.players_by_club[club1])} Spieler)")
        print(f"2. {club2} ({len(self.players_by_club[club2])} Spieler)")
        
        return club1, club2
        
    def run_two_club_negotiation(self, club1_name: str, club2_name: str,
                                strategy1: str = "balanced", strategy2: str = "balanced"):
        """Führt Verhandlung zwischen zwei Vereinen durch"""
        print("\n" + "=" * 70)
        print("STARTE VERHANDLUNG")
        print("=" * 70)
        
        # Erstelle Agenten
        club1 = ClubAgent(club1_name, strategy1)
        club2 = ClubAgent(club2_name, strategy2)
        
        # Setze Original-Spieler
        club1.set_original_players(self.players_by_club[club1_name])
        club2.set_original_players(self.players_by_club[club2_name])
        
        # Erstelle gemeinsamen Spielerpool
        all_players = (self.players_by_club[club1_name] + 
                      self.players_by_club[club2_name])
        
        club1.set_players(all_players)
        club2.set_players(all_players)
        
        print(f"\n{club1_name} - Strategie: {strategy1}")
        print(f"{club2_name} - Strategie: {strategy2}")
        print(f"Gesamt-Spielerpool: {len(all_players)} Spieler")
        
        # Mediator
        mediator = FootballMediator(len(all_players), len(all_players))
        
        # Initial Squad
        current_squad = mediator.init_squads()
        squad1_size = len(self.players_by_club[club1_name])
        
        # Start-Utilities
        print("\nStart-Situation:")
        print(f"{club1_name} Utility: {club1.evaluate_squad(current_squad[:squad1_size]):.2f}")
        print(f"{club2_name} Utility: {club2.evaluate_squad(current_squad[squad1_size:]):.2f}")
        
        # Verhandlungsschleife
        max_rounds = NEGOTIATION_CONFIG["MAX_ROUNDS"]
        successful_swaps = 0
        start_time = time.time()
        
        print(f"\nStarte {max_rounds} Verhandlungsrunden...")
        
        for round_num in range(max_rounds):
            # Vorschlag
            if round_num % 20 == 0 and round_num > 0:
                proposal = mediator.propose_team_shuffle(
                    current_squad,
                    NEGOTIATION_CONFIG["SHUFFLE_PERCENTAGE"]
                )
            else:
                proposal = mediator.propose_player_swap(current_squad)
                
            # Abstimmung
            club1_vote = club1.vote(current_squad[:squad1_size], proposal[:squad1_size])
            club2_vote = club2.vote(current_squad[squad1_size:], proposal[squad1_size:])
            
            if club1_vote and club2_vote:
                successful_swaps += 1
                current_squad = proposal
                
                # Progress Update
                if successful_swaps % NEGOTIATION_CONFIG["PROGRESS_INTERVAL_SWAPS"] == 0:
                    elapsed = time.time() - start_time
                    rate = (successful_swaps / (round_num + 1)) * 100
                    print(f"Runde {round_num:5d}: {successful_swaps:4d} Swaps "
                          f"({rate:5.1f}% Rate) - {elapsed:5.1f}s")
                    
        # Endergebnis
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("VERHANDLUNGSERGEBNIS")
        print("=" * 70)
        
        # End-Utilities
        final_utility1 = club1.evaluate_squad(current_squad[:squad1_size])
        final_utility2 = club2.evaluate_squad(current_squad[squad1_size:])
        
        print(f"\n{club1_name}:")
        print(f"  Final Utility: {final_utility1:.2f}")
        print(f"  Verbesserung: {final_utility1 - club1.evaluate_squad(list(range(squad1_size))):.2f}")
        
        print(f"\n{club2_name}:")
        print(f"  Final Utility: {final_utility2:.2f}")
        print(f"  Verbesserung: {final_utility2 - club2.evaluate_squad(list(range(squad1_size, len(all_players)))):.2f}")
        
        print(f"\nStatistiken:")
        print(f"  Dauer: {duration:.2f} Sekunden")
        print(f"  Erfolgreiche Swaps: {successful_swaps}")
        print(f"  Erfolgsrate: {(successful_swaps/max_rounds)*100:.2f}%")
        print(f"  Swaps/Sekunde: {successful_swaps/duration:.2f}")
        
        # Zeige einige finale Spieler
        print(f"\nTop 5 Spieler {club1_name} (nach Transfer):")
        club1_final = [all_players[i] for i in current_squad[:squad1_size]]
        club1_final.sort(key=lambda p: club1.evaluate_player(p), reverse=True)
        
        for i, player in enumerate(club1_final[:5], 1):
            original = "✅" if player.club == club1_name else "🔄"
            print(f"  {i}. {original} {player.name} ({player.club})")
            
    def run_market_simulation(self):
        """Simuliert einen kompletten Transfermarkt"""
        print("\n" + "=" * 70)
        print("TRANSFERMARKT-SIMULATION")
        print("=" * 70)
        
        # Wähle mehrere Vereine
        eligible_clubs = PlayerDataLoader.get_clubs_with_min_players(
            self.players_by_club,
            SYSTEM_CONFIG["MIN_PLAYERS_PER_CLUB"]
        )[:10]  # Top 10 Vereine
        
        print(f"Simuliere Transfermarkt mit {len(eligible_clubs)} Vereinen")
        
        # Erstelle Agenten für alle Vereine
        for club_name in eligible_clubs:
            strategy = random.choice(["balanced", "offensive", "defensive", "technical"])
            self.clubs[club_name] = ClubAgent(club_name, strategy)
            self.clubs[club_name].set_original_players(self.players_by_club[club_name])
            print(f"- {club_name}: {strategy} Strategie")
            
        # Erstelle Transfermarkt
        market = TransferMarket(self.clubs)
        
        # Simuliere Transfers
        print(f"\nSimuliere {TRANSFER_CONFIG['MAX_TRANSFERS_PER_CLUB']} Transfers...")
        results = market.simulate_transfer_window(
            max_transfers=50,
            rounds=1000
        )
        
        print(f"\nErgebnis:")
        print(f"- Erfolgreiche Transfers: {results['successful_transfers']}")
        print(f"- Erfolgsrate: {results['success_rate']:.1f}%")
        
        # Zeige Transfer-Bilanz
        print(f"\nTransfer-Bilanz:")
        for club, stats in results['transfer_summary'].items():
            print(f"{club:<30} In: {stats['transfers_in']:2d}, "
                  f"Out: {stats['transfers_out']:2d}, "
                  f"Netto: {stats['net_transfers']:+2d}")


def main():
    """Hauptfunktion"""
    print("⚽ FUSSBALL-TRANSFERSYSTEM ⚽")
    print("Version 2.0 - Mit echten Vereinen\n")
    
    system = TransferNegotiationSystem()
    
    # Lade Daten
    system.load_data()
    
    # Menü
    print("\n" + "=" * 70)
    print("OPTIONEN:")
    print("1. Verhandlung zwischen 2 Vereinen")
    print("2. Transfermarkt-Simulation (mehrere Vereine)")
    print("3. Beenden")
    print("=" * 70)
    
    # Für Demo: Option 1
    choice = "1"  # Oder input("Wähle Option (1-3): ")
    
    if choice == "1":
        # Zwei-Vereine-Verhandlung
        club1, club2 = system.select_clubs()
        
        # Strategien
        strategies = ["balanced", "offensive", "defensive", "technical"]
        strategy1 = random.choice(strategies)
        strategy2 = random.choice(strategies)
        
        system.run_two_club_negotiation(club1, club2, strategy1, strategy2)
        
    elif choice == "2":
        # Markt-Simulation
        system.run_market_simulation()
        
    else:
        print("Auf Wiedersehen!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgramm durch Benutzer beendet.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()