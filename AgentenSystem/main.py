#!/usr/bin/env python3
"""
Hauptmodul des Club-Basierten Fußball-Verhandlungssystems.

Dieses Skript steuert den gesamten Ablauf einer Fußballspieler-Verhandlungssimulation
zwischen zwei Vereinen. Es umfasst das Laden der Spielerdaten, die Initialisierung der
Vereinsagenten (Käufer und Verkäufer) und des Mediators, die Durchführung der
Verhandlungsrunden sowie die abschließende Ergebnisanalyse und -darstellung.

Hauptfunktionen des Moduls:
- `main()`: Orchestriert den gesamten Verhandlungsprozess.
- `load_club_data_with_validation()`: Lädt und validiert Spielerdaten für die Clubs.
- `create_club_agents_with_data()`: Erstellt und initialisiert die Agenten der Clubs.
- `run_club_negotiation()`: Führt die eigentliche Verhandlungssimulation durch.
- Hilfsfunktionen zur Darstellung von Clubzielen, Verhandlungsfortschritt und Ergebnissen.

Die Konfiguration des Systems erfolgt zentral über die Datei `config.py`.
Das System ist darauf ausgelegt, realistische Verhandlungsszenarien mit echten
Club-Daten und unterschiedlichen Kadergrößen zu simulieren.
"""

# Importiere alle Konfigurationen aus der zentralen config.py Datei.
# Dies macht alle Konfigurationsvariablen direkt im Namespace verfügbar.
from config import * 

# Importiere die notwendigen Klassen aus anderen Modulen des AgentenSystems.
from PlayerAgent import Player # Import der Player-Klasse für Typ-Annotationen und Instanziierung.
from BuyerClubAgent import BuyerClubAgent
from SellerClubAgent import SellerClubAgent
from PlayerDataLoader import ClubBasedPlayerDataLoader
from FootballMediator import ClubBasedFootballMediator
import time       # Für Zeitmessungen, z.B. Verhandlungsdauer.
import statistics # Für statistische Berechnungen (aktuell nicht explizit verwendet, aber potenziell nützlich).


def print_club_objectives_transparent() -> None:
    """
    Zeigt die (normalerweise als geheim betrachteten) Zielfunktionen und Strategien
    der beiden verhandelnden Clubs auf der Konsole an.

    Diese Funktion dient der Transparenz und dem besseren Verständnis des Systems,
    indem sie offenlegt, welche Attribute und Präferenzen die Agenten bei ihren
    Entscheidungen leiten. Die Anzeige erfolgt nur, wenn in `DISPLAY_CONFIG` aktiviert.
    """
    # Überprüfe, ob die Anzeige der Club-Ziele in der Konfiguration aktiviert ist.
    if not DISPLAY_CONFIG.get("SHOW_CLUB_OBJECTIVES", True):
        return # Tue nichts, wenn die Anzeige deaktiviert ist.
    
    print("\n" + "="*70)
    print("🎯 CLUB-ZIELFUNKTIONEN (NORMALERWEISE GEHEIM!)")
    print("="*70)
    
    # Hole Club-Namen und Attribut-Gewichtungen aus der Konfiguration.
    # Die `.get()` Methode wird verwendet, um Standardwerte bereitzustellen, falls Schlüssel fehlen.
    buyer_name = CLUB_CONFIG.get("BUYER_CLUB_NAME", "Käufer Club")
    buyer_attrs_config = BUYER_CONFIG.get("ATTRIBUTE_WEIGHTS", {})
    
    print(f"\n{buyer_name} - KÄUFER-STRATEGIE (aus Konfiguration):")
    print("-" * 50)
    print("🎯 Hauptziel (typisch): Offensive Stärke und technische Fähigkeiten maximieren.")
    print("📊 Bevorzugte Attribute (Top 5 basierend auf Gewichtung):")
    
    # Sortiere die Attribute des Käufers nach ihrer Gewichtung und zeige die Top 5 an.
    top_buyer_attrs = sorted(buyer_attrs_config.items(), key=lambda item: item[1], reverse=True)[:5]
    for attr, weight in top_buyer_attrs:
        print(f"   • {attr.replace('_', ' ').title()}: {weight:.1f}") # Formatiere Attributnamen für bessere Lesbarkeit.
    
    print("🏃 Positions-Präferenz (typisch): Höhere Gewichtung für vordere/offensive Positionen.")
    print("💭 Taktische Ausrichtung (Beispiel): Sucht Spieler, die das Angriffsspiel beleben.")
    
    seller_name = CLUB_CONFIG.get("SELLER_CLUB_NAME", "Verkäufer Club")
    seller_attrs_config = SELLER_CONFIG.get("ATTRIBUTE_WEIGHTS", {})

    print(f"\n{seller_name} - VERKÄUFER-STRATEGIE (aus Konfiguration):")
    print("-" * 50)
    print("🎯 Hauptziel (typisch): Defensive Stabilität sichern und/oder Transfererlöse maximieren.")
    print("📊 Bevorzugte Attribute (Top 5 basierend auf Gewichtung):")
    
    top_seller_attrs = sorted(seller_attrs_config.items(), key=lambda item: item[1], reverse=True)[:5]
    for attr, weight in top_seller_attrs:
        print(f"   • {attr.replace('_', ' ').title()}: {weight:.1f}")
        
    print("🛡️ Positions-Präferenz (typisch): Starke Verteidiger und Schlüsselspieler halten.")
    print("💭 Taktische Ausrichtung (Beispiel): Legt Wert auf robuste und vielseitige Spieler.")
    
    # Konflikt-Analyse
    print(f"\n⚔️ KONFLIKT-ANALYSE:")
    print("-" * 50)
    print("Beide Clubs wollen ihre besten Spieler in frühen Positionen!")
    print("Käufer bevorzugt: Angriff & Technik")
    print("Verkäufer bevorzugt: Defense & Vielseitigkeit")
    print("➡️ Unterschiedliche Präferenzen können zu interessanten Verhandlungsdynamiken führen.")
    
    print("="*70)


def load_club_data_with_validation() -> Tuple[Tuple[List[Player], List[Player]], Tuple[str, str]]:
    """
    Lädt Spielerdaten für Käufer- und Verkäufer-Clubs aus der CSV-Datei.
    Führt eine Validierung der Club-Konfiguration durch und bestimmt die finalen Club-Namen.

    Returns:
        Tuple[Tuple[List[Player], List[Player]], Tuple[str, str]]: 
            Ein Tupel, bestehend aus:
            - Einem inneren Tupel mit den Spielerlisten: `(buyer_players, seller_players)`
            - Einem inneren Tupel mit den finalen Club-Namen: `(buyer_club_name, seller_club_name)`
    
    Raises:
        Exception: Fängt und leitet alle Exceptions weiter, die während des Datenladens
                   oder der Konfigurationsvalidierung auftreten können (z.B. `FileNotFoundError`),
                   nachdem eine Fehlermeldung ausgegeben wurde.
    """
    print("🔄 LADE SPIELERDATEN FÜR CLUBS...")
    
    # Validiere die grundlegende Club-Konfiguration aus `config.py`.
    config_is_valid = validate_club_config() # Diese Funktion ist in config.py definiert.
    if not config_is_valid and DEBUG_CONFIG.get("DEBUG_MODE", False):
        # Nur im Debug-Modus fortfahren, wenn die Konfiguration Warnungen erzeugt.
        print("⚠️ WARNUNG: Club-Konfiguration hat Validierungswarnungen. Fortfahren im Debug-Modus...")
    
    try:
        # Lade die Spielerlisten für Käufer und Verkäufer mithilfe des PlayerDataLoaders.
        # `load_clubs_from_csv` verwendet Standardwerte aus `CLUB_CONFIG`, wenn keine Argumente übergeben werden.
        buyer_players, seller_players = ClubBasedPlayerDataLoader.load_clubs_from_csv()
        
        # Bestimme die finalen Club-Namen. Diese können in `BUYER_CONFIG` oder `SELLER_CONFIG`
        # überschrieben werden oder fallen auf die globalen Namen in `CLUB_CONFIG` zurück.
        final_buyer_club_name = BUYER_CONFIG.get("CLUB_NAME") or CLUB_CONFIG.get("BUYER_CLUB_NAME", "Käufer")
        final_seller_club_name = SELLER_CONFIG.get("CLUB_NAME") or CLUB_CONFIG.get("SELLER_CLUB_NAME", "Verkäufer")
        
        return (buyer_players, seller_players), (final_buyer_club_name, final_seller_club_name)
        
    except Exception as e:
        # Gib eine Fehlermeldung aus und leite die Exception weiter, wenn das Laden fehlschlägt.
        print(f"❌ KRITISCHER FEHLER beim Laden der Club-Daten: {e}")
        if DEBUG_CONFIG.get("DEBUG_MODE", False):
            import traceback # Importiere traceback nur bei Bedarf.
            traceback.print_exc() # Gib den vollständigen Stacktrace im Debug-Modus aus.
        raise # Leite die Exception weiter, um den Prozess ggf. zu stoppen.


def create_club_agents_with_data(
    buyer_players: List[Player], 
    seller_players: List[Player], 
    buyer_name: str, 
    seller_name: str
) -> Tuple[BuyerClubAgent, SellerClubAgent]:
    """
    Erstellt und initialisiert die Agenten für den Käufer- und Verkäufer-Club.
    Den Agenten werden ihre jeweiligen Spielerlisten und Namen zugewiesen.

    Args:
        buyer_players (List[Player]): Die Liste der Spieler-Objekte für den Käufer-Club.
        seller_players (List[Player]): Die Liste der Spieler-Objekte für den Verkäufer-Club.
        buyer_name (str): Der Name des Käufer-Clubs.
        seller_name (str): Der Name des Verkäufer-Clubs.

    Returns:
        Tuple[BuyerClubAgent, SellerClubAgent]: Ein Tupel mit den initialisierten
                                                 `BuyerClubAgent`- und `SellerClubAgent`-Objekten.
    """
    print("\n🏗️ ERSTELLE CLUB-AGENTEN...")
    
    # Erstelle den Käufer-Club-Agenten und weise ihm seine Spieler zu.
    # Die Agenten-Konstruktor (`__init__`) nutzt `attribute_weights_override`, falls in der Streamlit-App gesetzt.
    buyer_club = BuyerClubAgent(club_name=buyer_name) 
    buyer_club.set_players(buyer_players)
    
    # Erstelle den Verkäufer-Club-Agenten und weise ihm seine Spieler zu.
    seller_club = SellerClubAgent(club_name=seller_name)
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
    
    # Speichere Kopien der initialen Spielerlisten (Player-Objekte) für die spätere Ergebnisanalyse.
    # `copy.deepcopy` wird hier nicht zwingend benötigt, wenn Player-Objekte selbst unveränderlich sind
    # oder ihre relevanten Attribute (wie Name, Alter) während der Verhandlung nicht direkt geändert werden.
    # `list.copy()` erstellt eine neue Liste, aber die Player-Objekte darin sind Referenzen.
    # Wenn Agenten ihre internen Player-Objekte modifizieren würden (was sie aktuell nicht tun),
    # wäre deepcopy für initial_xxx_players notwendig.
    initial_buyer_players = buyer_club.players.copy() 
    initial_seller_players = seller_club.players.copy()
    
    print(f"\n📋 START-AUFSTELLUNGEN (Spieleranzahl):")
    print(f"{buyer_club.club_name}: {len(buyer_club.players)} Spieler")
    print(f"{seller_club.club_name}: {len(seller_club.players)} Spieler")
    # Hinweis: `init_squads` im Mediator erstellt Index-basierte Listen, die hier nicht direkt
    # für die Utility-Berechnung der Agenten (die mit Player-Objekten arbeiten) verwendet werden.
    # Die Agenten verwalten ihre Spielerlisten (`self.players`) selbst.

    # Initiale Utility-Bewertungen
    print(f"\n💯 START-UTILITIES:")
    # Die `calculate_utility_for_hypothetical_squad` Methode wird verwendet, da sie direkt mit
    # der aktuellen Spielerliste des Agenten (`agent.players`) arbeitet.
    initial_buyer_utility = buyer_club.calculate_utility_for_hypothetical_squad(buyer_club.players)
    initial_seller_utility = seller_club.calculate_utility_for_hypothetical_squad(seller_club.players)
    print(f"{buyer_club.club_name}: {initial_buyer_utility:.2f}")
    print(f"{seller_club.club_name}: {initial_seller_utility:.2f}")
    
    # Verhandlungs-Schleife für Inter-Club Spielertausche
    accepted_inter_club_swaps = 0
    last_progress_swap_count = 0 # Verhindert mehrfache Ausgabe für denselben Swap-Meilenstein
    
    # Anmerkung: Intra-Team Positions-Swaps/Shuffles (mittels `mediator.propose_player_swap` 
    # oder `mediator.propose_team_shuffle` und `agent.evaluate_squad` mit Index-Listen) 
    # sind in dieser aktuellen Hauptschleife nicht aktiv, der Fokus liegt auf Inter-Club Tauschen.
    # Falls diese wieder aktiviert werden sollen, müssten sie als separate Phase oder
    # als Teil der Agenten-Entscheidungslogik (z.B. ob ein Agent seinen Kader intern anpasst,
    # bevor er einem Inter-Club-Tausch zustimmt) integriert werden.

    for round_num in range(max_rounds):
        # Mediator schlägt einen Tausch von Spieler-Objekten zwischen den Clubs vor.
        proposed_buyer_player, proposed_seller_player = mediator.propose_inter_club_swap()

        # Breche ab, wenn keine gültigen Tauschpartner mehr gefunden werden können (z.B. leere Pools).
        if proposed_buyer_player is None or proposed_seller_player is None:
            if LOGGING_CONFIG.get("SHOW_DETAILED_START_INFO", True):
                print(f"Runde {round_num+1:,}: Kein gültiger Inter-Club-Tauschvorschlag möglich (Pools zu klein?). Verhandlung beendet.")
            break 

        # Agenten bewerten den vorgeschlagenen Tausch und stimmen ab.
        # Die `vote`-Methode der Agenten wurde refaktorisiert, um `Player`-Objekte zu akzeptieren.
        buyer_accepted = buyer_club.vote(proposed_buyer_player, proposed_seller_player)
        # Für den Verkäufer sind die Rollen der Spieler im Tauschangebot vertauscht.
        seller_accepted = seller_club.vote(proposed_seller_player, proposed_buyer_player)

        trade_executed_this_round = False
        if buyer_accepted and seller_accepted:
            # Wenn beide Clubs zustimmen, führe den Tausch in den Spielerlisten der Agenten durch.
            try:
                # Entferne den abgegebenen Spieler und füge den erhaltenen Spieler hinzu.
                buyer_club.players.remove(proposed_buyer_player)
                buyer_club.players.append(proposed_seller_player) 
                seller_club.players.remove(proposed_seller_player)
                seller_club.players.append(proposed_buyer_player)
                
                accepted_inter_club_swaps += 1
                trade_executed_this_round = True
                # Detailliertes Logging für akzeptierte Trades, falls aktiviert.
                if LOGGING_CONFIG.get("SHOW_DETAILED_START_INFO", True): 
                    current_buyer_utility_after_trade = buyer_club.calculate_utility_for_hypothetical_squad(buyer_club.players)
                    current_seller_utility_after_trade = seller_club.calculate_utility_for_hypothetical_squad(seller_club.players)
                    print(f"🔄 Trade Akzeptiert! Runde {round_num+1}: "
                          f"{buyer_club.club_name} gibt {proposed_buyer_player.name} für {proposed_seller_player.name}. "
                          f"Neue Utility: {current_buyer_utility_after_trade:.2f}. | "
                          f"{seller_club.club_name} gibt {proposed_seller_player.name} für {proposed_buyer_player.name}. "
                          f"Neue Utility: {current_seller_utility_after_trade:.2f}.")
            except ValueError as e:
                # Dieser Fehler sollte selten auftreten, wenn die Spielerlisten korrekt verwaltet werden.
                print(f"FEHLER bei Trade-Ausführung in Runde {round_num+1}: {e}. Spieler nicht in Liste gefunden.")
                trade_executed_this_round = False
        
        # Protokolliere die Entscheidung des Mediators für diesen Tauschversuch.
        mediator.record_trade_decision(
            proposed_buyer_player, 
            proposed_seller_player,
            buyer_accepted, 
            seller_accepted, 
            trade_executed_this_round
        )
            
        # Fortschrittsanzeige basierend auf der Anzahl der akzeptierten Tausche.
        if accepted_inter_club_swaps > last_progress_swap_count and \
           accepted_inter_club_swaps % NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_SWAPS", 250) == 0:
            # Stelle sicher, dass der Fortschritt nur einmal pro Intervall-Trigger gedruckt wird.
            if trade_executed_this_round : 
                print_negotiation_progress(
                    round_num + 1, accepted_inter_club_swaps, buyer_club, seller_club
                )
                last_progress_swap_count = accepted_inter_club_swaps 
        
        # Runden-basierte Fortschrittsanzeige (nützlich, wenn wenige Tausche akzeptiert werden).
        if (round_num + 1) % NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_ROUNDS", 2000) == 0 and \
           (accepted_inter_club_swaps == last_progress_swap_count or \
            accepted_inter_club_swaps % NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_SWAPS", 250) != 0):
            # Nur drucken, wenn nicht gerade eine Swap-basierte Fortschrittsanzeige erfolgte.
            acceptance_rate = accepted_inter_club_swaps / (round_num + 1) * 100 if (round_num + 1) > 0 else 0
            print(f"\n--- Runde {round_num+1:,} / {max_rounds:,} ---")
            print(f"Akzeptierte Inter-Club Swaps bisher: {accepted_inter_club_swaps:,} (~{acceptance_rate:.1f}%)")
            # `minimal=True` sorgt für eine kompaktere Ausgabe der Fortschrittsdetails.
            print_negotiation_progress(round_num + 1, accepted_inter_club_swaps, buyer_club, seller_club, minimal=True)

    # Finale Ergebnisse nach Abschluss aller Verhandlungsrunden.
    print_final_negotiation_results(
        buyer_club, seller_club, 
        initial_buyer_players, initial_seller_players, # Übergabe der initialen Spielerlisten
        buyer_club.players, seller_club.players,       # Übergabe der finalen Spielerlisten
        accepted_inter_club_swaps, max_rounds, start_time
    )


def print_negotiation_progress(
    round_num: int, accepted_swaps: int, 
    buyer_club: BuyerClubAgent, seller_club: SellerClubAgent, 
    minimal: bool = False
):
    """
    Gibt den aktuellen Fortschritt der Verhandlung auf der Konsole aus.
    Dies beinhaltet die aktuelle Runde, Anzahl akzeptierter Tausche, aktuelle Utility-Werte
    der Clubs und optional weitere Details wie Agenten-Temperaturen und Kader-Frontaufstellungen.

    Args:
        round_num (int): Die aktuelle Verhandlungsrunde.
        accepted_swaps (int): Die Anzahl der bisher akzeptierten Inter-Club Tausche.
        buyer_club (BuyerClubAgent): Der Agent des Käufer-Clubs.
        seller_club (SellerClubAgent): Der Agent des Verkäufer-Clubs.
        minimal (bool, optional): Wenn True, wird eine kompaktere Fortschrittsanzeige ausgegeben.
                                  Standardmäßig False für eine detailliertere Ausgabe.
    """
    if not minimal: # Full progress output
        print(f"\n{'-'*50}")
        print(f"📍 Runde {round_num:,}, Akzeptierte Inter-Club Swaps: {accepted_swaps:,}")
        print(f"{'-'*50}")
    
    current_buyer_utility = buyer_club.calculate_utility_for_hypothetical_squad(buyer_club.players)
    current_seller_utility = seller_club.calculate_utility_for_hypothetical_squad(seller_club.players)
    print(f"💯 Aktuelle Utilities: {buyer_club.club_name}={current_buyer_utility:.2f}, {seller_club.club_name}={current_seller_utility:.2f}")
    
    # Temperatur-Info
    if LOGGING_CONFIG.get("SHOW_TEMPERATURE_UPDATES", False) and not minimal:
        print(f"🌡️ Temperaturen:")
        print(f"   {buyer_club.club_name}: {buyer_club.t:.2f}")
        print(f"   {seller_club.club_name}: {seller_club.t:.2f}")
    
    # Beispiel aktuelle Aufstellungen (erste 5 Positionen)
    if not minimal:
        print(f"📋 Aktuelle Spielerlisten (Top 5 Spieler):")
        buyer_front_names = [p.name for p in buyer_club.players[:5]]
        seller_front_names = [p.name for p in seller_club.players[:5]]
        print(f"   {buyer_club.club_name} ({len(buyer_club.players)} Spieler): {', '.join(buyer_front_names) if buyer_front_names else 'N/A'}")
        print(f"   {seller_club.club_name} ({len(seller_club.players)} Spieler): {', '.join(seller_front_names) if seller_front_names else 'N/A'}")


def print_final_negotiation_results(
    buyer_club, seller_club, initial_buyer_players_list: List[Player], initial_seller_players_list: List[Player],
    final_buyer_players_list: List[Player], final_seller_players_list: List[Player], 
    accepted_swaps, max_rounds, start_time
):
    """
    Zeigt ausführliche finale Verhandlungsergebnisse.
    Nimmt jetzt Listen von Player-Objekten.
    """
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*70)
    print("🏁 FINALE VERHANDLUNGS-ERGEBNISSE")
    print("="*70)
    
    # Finale Aufstellungen (Spielernamen)
    print(f"🎯 FINALE SPIELERLISTEN:")
    final_buyer_names = [p.name for p in final_buyer_players_list]
    final_seller_names = [p.name for p in final_seller_players_list]
    print(f"{buyer_club.club_name} ({len(final_buyer_players_list)} Spieler): {final_buyer_names[:15]}..." if len(final_buyer_names) > 15 else final_buyer_names)
    print(f"{seller_club.club_name} ({len(final_seller_players_list)} Spieler): {final_seller_names[:15]}..." if len(final_seller_names) > 15 else final_seller_names)
    
    # Finale Utilities
    final_buyer_utility = buyer_club.calculate_utility_for_hypothetical_squad(final_buyer_players_list)
    final_seller_utility = seller_club.calculate_utility_for_hypothetical_squad(final_seller_players_list)
    initial_buyer_utility = buyer_club.calculate_utility_for_hypothetical_squad(initial_buyer_players_list)
    initial_seller_utility = seller_club.calculate_utility_for_hypothetical_squad(initial_seller_players_list)
    
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
        # Mediator now takes the actual player lists (pools) from the clubs
        print(f"\n🔗 ERSTELLE MEDIATOR...")
        mediator = ClubBasedFootballMediator(
            buyer_club.players, seller_club.players
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