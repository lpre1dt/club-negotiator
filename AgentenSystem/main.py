#!/usr/bin/env python3
"""
CLUB-BASIERTES FUßBALL-VERHANDLUNGSSYSTEM
==========================================

Dieses System simuliert realistische Verhandlungen zwischen zwei echten 
Fußball-Clubs über ihre Squad-Aufstellungen.

Wichtige Features:
- Echte Clubs aus CSV-Daten
- Unterschiedliche Squad-Größen
- Transparente Club-Zielfunktionen  
- Intelligent behandelte Größenunterschiede
- Vollständig konfigurierbar

Konfiguration erfolgt vollständig über config.py
"""

# Import der zentralen Konfiguration
from config import *

from BuyerClubAgent import BuyerClubAgent
from SellerClubAgent import SellerClubAgent
from PlayerDataLoader import ClubBasedPlayerDataLoader
from FootballMediator import ClubBasedFootballMediator
import time
import statistics


def print_club_objectives_transparent():
    """
    Zeigt die normalerweise geheimen Zielfunktionen beider Clubs
    
    Dies macht die Verhandlung transparent und hilft beim Verständnis
    warum bestimmte Entscheidungen getroffen werden.
    """
    if not DISPLAY_CONFIG.get("SHOW_CLUB_OBJECTIVES", True):
        return
    
    print("\n" + "="*70)
    print("🎯 CLUB-ZIELFUNKTIONEN (NORMALERWEISE GEHEIM!)")
    print("="*70)
    
    # Käufer-Club Ziele
    buyer_name = CLUB_CONFIG["BUYER_CLUB_NAME"]
    print(f"\n{buyer_name} - KÄUFER-STRATEGIE:")
    print("-" * 50)
    print("🎯 Hauptziel: Offensive Power maximieren")
    print("📊 Bevorzugte Attribute:")
    
    # Top 5 Attribute für Käufer
    buyer_attrs = BUYER_CONFIG["ATTRIBUTE_WEIGHTS"]
    top_buyer_attrs = sorted(buyer_attrs.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for attr, weight in top_buyer_attrs:
        print(f"   • {attr.replace('_', ' ').title()}: {weight:.1f}")
    
    print("🏃 Positions-Präferenz: Hohe Gewichtung für frühe Positionen")
    print("💭 Geheime Tactic: Will technische und offensive Spieler vorne")
    
    # Verkäufer-Club Ziele  
    seller_name = CLUB_CONFIG["SELLER_CLUB_NAME"]
    print(f"\n{seller_name} - VERKÄUFER-STRATEGIE:")
    print("-" * 50)
    print("🎯 Hauptziel: Defensive Stabilität maximieren")
    print("📊 Bevorzugte Attribute:")
    
    # Top 5 Attribute für Verkäufer
    seller_attrs = SELLER_CONFIG["ATTRIBUTE_WEIGHTS"] 
    top_seller_attrs = sorted(seller_attrs.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for attr, weight in top_seller_attrs:
        print(f"   • {attr.replace('_', ' ').title()}: {weight:.1f}")
    
    print("🛡️ Positions-Präferenz: Hohe Gewichtung für frühe Positionen")
    print("💭 Geheime Tactic: Will defensive und vielseitige Spieler vorne")
    
    # Konflikt-Analyse
    print(f"\n⚔️ KONFLIKT-ANALYSE:")
    print("-" * 50)
    print("Beide Clubs wollen ihre besten Spieler in frühen Positionen!")
    print("Käufer bevorzugt: Angriff & Technik")
    print("Verkäufer bevorzugt: Defense & Vielseitigkeit")
    print("➡️ Dies führt zu spannenden Verhandlungen!")
    
    print("="*70)


def load_club_data_with_validation():
    """
    Lädt Club-Daten aus der CSV mit vollständiger Validierung
    
    Returns:
        Tuple[Tuple[List[Player], List[Player]], Tuple[str, str]]: 
        ((Käufer-Spieler, Verkäufer-Spieler), (Käufer-Name, Verkäufer-Name))
    """
    print("🔄 LADE CLUB-DATEN...")
    
    # Validiere Club-Konfiguration
    config_valid = validate_club_config()
    if not config_valid and DEBUG_CONFIG.get("DEBUG_MODE", False):
        print("⚠️ Konfiguration hat Probleme, fahre trotzdem fort...")
    
    # Lade Spieler für beide Clubs
    try:
        buyer_players, seller_players = ClubBasedPlayerDataLoader.load_clubs_from_csv()
        
        # Bestimme finale Club-Namen
        buyer_club_name = BUYER_CONFIG.get("CLUB_NAME") or CLUB_CONFIG["BUYER_CLUB_NAME"]
        seller_club_name = SELLER_CONFIG.get("CLUB_NAME") or CLUB_CONFIG["SELLER_CLUB_NAME"]
        
        return (buyer_players, seller_players), (buyer_club_name, seller_club_name)
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Club-Daten: {e}")
        
        if DEBUG_CONFIG.get("DEBUG_MODE", False):
            import traceback
            traceback.print_exc()
        
        raise


def create_club_agents_with_data(buyer_players, seller_players, buyer_name, seller_name):
    """
    Erstellt die Club-Agenten und setzt ihre Spieler-Daten
    
    Args:
        buyer_players: Liste der Käufer-Spieler
        seller_players: Liste der Verkäufer-Spieler
        buyer_name: Name des Käufer-Clubs
        seller_name: Name des Verkäufer-Clubs
        
    Returns:
        Tuple[BuyerClubAgent, SellerClubAgent]: Die konfigurierten Club-Agenten
    """
    print("\n🏗️ ERSTELLE CLUB-AGENTEN...")
    
    # Erstelle Käufer-Club mit übergebenem Namen
    buyer_club = BuyerClubAgent(buyer_name)
    buyer_club.set_players(buyer_players)
    
    # Erstelle Verkäufer-Club mit übergebenem Namen  
    seller_club = SellerClubAgent(seller_name)
    seller_club.set_players(seller_players)
    
    # Zeige Club-Informationen
    print(f"✅ {buyer_club.club_name}: {len(buyer_players)} Spieler")
    print(f"✅ {seller_club.club_name}: {len(seller_players)} Spieler")
    
    # Kurze Spieler-Bewertungs-Demonstration
    if DISPLAY_CONFIG.get("SHOW_DETAILED_START_INFO", True):
        print(f"\n📊 SPIELER-BEWERTUNGS-PREVIEW:")
        num_examples = min(3, len(buyer_players), len(seller_players))
        
        print("Beispiel - Wie die Clubs ihre eigenen Spieler bewerten:")
        print("-" * 60)
        
        for i in range(num_examples):
            buyer_player = buyer_players[i]
            buyer_rating = buyer_club.evaluate_player(buyer_player)
            print(f"{buyer_name}: {buyer_player.name:<25} = {buyer_rating:6.1f}")
            
            seller_player = seller_players[i]
            seller_rating = seller_club.evaluate_player(seller_player)
            print(f"{seller_name}: {seller_player.name:<25} = {seller_rating:6.1f}")
            print()
    
    return buyer_club, seller_club


def run_club_negotiation(buyer_club, seller_club, mediator):
    """
    Führt die Club-Verhandlung mit erweiterten Statistiken durch
    
    Args:
        buyer_club: Käufer-Club-Agent
        seller_club: Verkäufer-Club-Agent
        mediator: Club-basierter Mediator
    """
    max_rounds = NEGOTIATION_CONFIG["MAX_ROUNDS"]
    start_time = time.time()
    
    print("\n" + "="*70)
    print("🚀 CLUB-VERHANDLUNG GESTARTET")
    print("="*70)
    print(f"Käufer: {buyer_club.club_name}")
    print(f"Verkäufer: {seller_club.club_name}")
    print(f"Max. Runden: {max_rounds:,}")
    
    # Initiale Squad-Aufstellungen für beide Clubs
    buyer_squad, seller_squad = mediator.init_squads()
    initial_buyer_squad = buyer_squad.copy()
    initial_seller_squad = seller_squad.copy()
    
    print(f"\n📋 START-AUFSTELLUNGEN:")
    print(f"{buyer_club.club_name}: {buyer_squad}")
    print(f"{seller_club.club_name}: {seller_squad}")
    
    # Initiale Utility-Bewertungen
    print(f"\n💯 START-UTILITIES:")
    buyer_utility = buyer_club.evaluate_squad(buyer_squad)
    seller_utility = seller_club.evaluate_squad(seller_squad)
    print(f"{buyer_club.club_name}: {buyer_utility:.2f}")
    print(f"{seller_club.club_name}: {seller_utility:.2f}")
    
    # Verhandlungs-Schleife
    accepted_swaps = 0
    last_progress_round = 0
    
    for round_num in range(max_rounds):
        # Bestimme Art des Vorschlags
        shuffle_freq = NEGOTIATION_CONFIG.get("TEAM_SHUFFLE_FREQUENCY", 0.01)
        if round_num % round(1 / shuffle_freq) == 0:
            # Team-Shuffle mit konfigurierbarem Prozentsatz
            shuffle_pct = NEGOTIATION_CONFIG.get("SHUFFLE_PERCENTAGE", 0.2)
            proposed_buyer, proposed_seller = mediator.propose_team_shuffle(
                buyer_squad, seller_squad, shuffle_pct
            )
        else:
            # Einfacher Spieler-Swap
            proposed_buyer, proposed_seller = mediator.propose_player_swap(
                buyer_squad, seller_squad
            )
        
        # Beide Clubs abstimmen lassen
        buyer_vote = buyer_club.vote(buyer_squad, proposed_buyer)
        seller_vote = seller_club.vote(seller_squad, proposed_seller)
        
        # Swap wird nur akzeptiert wenn beide Clubs zustimmen
        if buyer_vote and seller_vote:
            buyer_squad = proposed_buyer
            seller_squad = proposed_seller
            accepted_swaps += 1
            
            # Fortschritts-Anzeige
            if accepted_swaps % NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_SWAPS", 250) == 0:
                print_negotiation_progress(
                    round_num, accepted_swaps, buyer_club, seller_club,
                    buyer_squad, seller_squad
                )
                last_progress_round = round_num
        
        # Runden-basierte Fortschritts-Anzeige
        round_interval = NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_ROUNDS", 2000)
        if round_num % round_interval == 0 and round_num > last_progress_round:
            acceptance_rate = accepted_swaps / (round_num + 1) * 100
            print(f"Runde {round_num:,}: {accepted_swaps:,} Swaps (~{acceptance_rate:.1f}%)")
    
    # Finale Ergebnisse
    print_final_negotiation_results(
        buyer_club, seller_club, initial_buyer_squad, initial_seller_squad,
        buyer_squad, seller_squad, accepted_swaps, max_rounds, start_time
    )


def print_negotiation_progress(
    round_num, accepted_swaps, buyer_club, seller_club, 
    buyer_squad, seller_squad
):
    """
    Zeigt Fortschritt der Verhandlung an
    """
    print(f"\n{'-'*50}")
    print(f"📍 Runde {round_num:,}, Akzeptierte Swaps: {accepted_swaps:,}")
    print(f"{'-'*50}")
    
    # Aktuelle Utilities
    buyer_utility = buyer_club.evaluate_squad(buyer_squad)
    seller_utility = seller_club.evaluate_squad(seller_squad)
    print(f"💯 Aktuelle Utilities:")
    print(f"   {buyer_club.club_name}: {buyer_utility:.2f}")
    print(f"   {seller_club.club_name}: {seller_utility:.2f}")
    
    # Temperatur-Info
    if LOGGING_CONFIG.get("SHOW_TEMPERATURE_UPDATES", False):
        print(f"🌡️ Temperaturen:")
        print(f"   {buyer_club.club_name}: {buyer_club.t:.2f}")
        print(f"   {seller_club.club_name}: {seller_club.t:.2f}")
    
    # Beispiel aktuelle Aufstellungen (erste 5 Positionen)
    print(f"📋 Aktuelle Front-Aufstellungen:")
    buyer_front = buyer_squad[:5]
    seller_front = seller_squad[:5]
    print(f"   {buyer_club.club_name}: {buyer_front}")
    print(f"   {seller_club.club_name}: {seller_front}")


def print_final_negotiation_results(
    buyer_club, seller_club, initial_buyer_squad, initial_seller_squad,
    final_buyer_squad, final_seller_squad, accepted_swaps, max_rounds, start_time
):
    """
    Zeigt ausführliche finale Verhandlungsergebnisse
    """
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*70)
    print("🏁 FINALE VERHANDLUNGS-ERGEBNISSE")
    print("="*70)
    
    # Finale Aufstellungen
    print(f"🎯 FINALE SQUADS:")
    print(f"{buyer_club.club_name}: {final_buyer_squad}")
    print(f"{seller_club.club_name}: {final_seller_squad}")
    
    # Finale Utilities
    final_buyer_utility = buyer_club.evaluate_squad(final_buyer_squad)
    final_seller_utility = seller_club.evaluate_squad(final_seller_squad)
    initial_buyer_utility = buyer_club.evaluate_squad(initial_buyer_squad)
    initial_seller_utility = seller_club.evaluate_squad(initial_seller_squad)
    
    print(f"\n💯 UTILITY-ENTWICKLUNG:")
    print(f"{buyer_club.club_name}:")
    print(f"   Start: {initial_buyer_utility:.2f}")
    print(f"   Ende:  {final_buyer_utility:.2f}")
    print(f"   Δ:     {final_buyer_utility - initial_buyer_utility:+.2f}")
    
    print(f"{seller_club.club_name}:")
    print(f"   Start: {initial_seller_utility:.2f}")  
    print(f"   Ende:  {final_seller_utility:.2f}")
    print(f"   Δ:     {final_seller_utility - initial_seller_utility:+.2f}")
    
    # Verhandlungs-Statistiken
    print(f"\n📊 VERHANDLUNGS-STATISTIKEN:")
    print(f"Akzeptierte Swaps: {accepted_swaps:,} von {max_rounds:,}")
    print(f"Akzeptanzrate: {accepted_swaps/max_rounds*100:.2f}%")
    print(f"Verhandlungsdauer: {duration:.2f} Sekunden")
    print(f"Runden/Sekunde: {max_rounds/duration:.0f}")
    
    # Analyse der Verhandlung
    analyze_negotiation_outcome(
        buyer_club, seller_club, initial_buyer_squad, initial_seller_squad,
        final_buyer_squad, final_seller_squad
    )


def analyze_negotiation_outcome(
    buyer_club, seller_club, initial_buyer_squad, initial_seller_squad,
    final_buyer_squad, final_seller_squad
):
    """
    Analysiert das Verhandlungsergebnis im Detail
    """
    if not ANALYSIS_CONFIG.get("ANALYZE_POSITION_PREFERENCES", True):
        return
    
    print(f"\n🔍 VERHANDLUNGS-ANALYSE:")
    print("-" * 50)
    
    # Analysiere Positions-Änderungen
    buyer_changes = sum(
        1 for i in range(len(final_buyer_squad))
        if initial_buyer_squad[i] != final_buyer_squad[i]
    )
    seller_changes = sum(
        1 for i in range(len(final_seller_squad))
        if initial_seller_squad[i] != final_seller_squad[i]
    )
    
    print(f"Positions-Änderungen:")
    print(f"   {buyer_club.club_name}: {buyer_changes}/{len(final_buyer_squad)} ({buyer_changes/len(final_buyer_squad)*100:.1f}%)")
    print(f"   {seller_club.club_name}: {seller_changes}/{len(final_seller_squad)} ({seller_changes/len(final_seller_squad)*100:.1f}%)")
    
    # Wer hat "gewonnen"?
    buyer_improvement = buyer_club.evaluate_squad(final_buyer_squad) - buyer_club.evaluate_squad(initial_buyer_squad)
    seller_improvement = seller_club.evaluate_squad(final_seller_squad) - seller_club.evaluate_squad(initial_seller_squad)
    
    print(f"\n🏆 VERHANDLUNGS-GEWINNER:")
    if buyer_improvement > seller_improvement:
        print(f"   {buyer_club.club_name} hat mehr profitiert (+{buyer_improvement:.2f})")
    elif seller_improvement > buyer_improvement:
        print(f"   {seller_club.club_name} hat mehr profitiert (+{seller_improvement:.2f})")
    else:
        print(f"   Ausgeglichenes Ergebnis (beide ~+{buyer_improvement:.2f})")
    
    # Temperatur-Endwerte
    print(f"\n🌡️ FINALE TEMPERATUREN:")
    print(f"   {buyer_club.club_name}: {buyer_club.t:.3f}")
    print(f"   {seller_club.club_name}: {seller_club.t:.3f}")


def main():
    """
    Hauptfunktion des Club-basierten Verhandlungssystems
    """
    print("="*70)
    print("🏟️ CLUB-BASIERTES FUßBALL-VERHANDLUNGSSYSTEM")
    print("="*70)
    print("Echte Club-Verhandlungen mit realistischen Squads")
    print("Vollständig konfigurierbar über config.py")
    print("="*70)
    
    try:
        # 1. Lade Club-Daten und validiere
        (buyer_players, seller_players), (buyer_name, seller_name) = load_club_data_with_validation()
        
        # 2. Zeige transparente Club-Zielfunktionen
        print_club_objectives_transparent()
        
        # 3. Erstelle Club-Agenten mit Daten
        buyer_club, seller_club = create_club_agents_with_data(
            buyer_players, seller_players, buyer_name, seller_name
        )
        
        # 4. Erstelle Club-basierten Mediator
        print(f"\n🔗 ERSTELLE MEDIATOR...")
        mediator = ClubBasedFootballMediator(
            len(buyer_players), len(seller_players)
        )
        
        # 5. Validiere Mediator-Statistiken
        mediator_stats = mediator.get_negotiation_statistics()
        print(f"✅ Mediator konfiguriert:")
        for key, value in mediator_stats.items():
            print(f"   {key}: {value}")
        
        # 6. Starte Club-Verhandlung
        print(f"\n🚀 STARTE CLUB-VERHANDLUNG...")
        run_club_negotiation(buyer_club, seller_club, mediator)
        
        print(f"\n🎉 VERHANDLUNG ERFOLGREICH ABGESCHLOSSEN!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Verhandlung durch Benutzer abgebrochen")
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        if DEBUG_CONFIG.get("DEBUG_MODE", False):
            import traceback
            traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)