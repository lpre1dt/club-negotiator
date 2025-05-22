#!/usr/bin/env python3
"""
FUSSBALL-VERHANDLUNGSSYSTEM MIT ERWEITERTEN STATISTIKEN
Zentral konfigurierbar über config.py
"""

# Import der zentralen Konfiguration
from config import *

from BuyerClubAgent import BuyerClubAgent
from SellerClubAgent import SellerClubAgent
from FootballMediator import FootballMediator
from PlayerDataLoader import PlayerDataLoader
import time
import statistics


class NegotiationAnalyzer:
    """Analysiert und protokolliert Verhandlungsstatistiken"""

    def __init__(self):
        self.history = []
        self.utility_history_buyer = []
        self.utility_history_seller = []
        self.temperature_history_buyer = []
        self.temperature_history_seller = []
        self.acceptance_rates_over_time = []

    def record_swap(
        self,
        round_num,
        squad,
        buyer_utility,
        seller_utility,
        buyer_temp,
        seller_temp,
        accepted_count,
        total_proposals,
    ):
        """Protokolliert einen Swap"""
        self.history.append(
            {
                "round": round_num,
                "squad": squad.copy(),
                "buyer_utility": buyer_utility,
                "seller_utility": seller_utility,
                "buyer_temp": buyer_temp,
                "seller_temp": seller_temp,
                "acceptance_rate": accepted_count / max(total_proposals, 1),
            }
        )

        self.utility_history_buyer.append(buyer_utility)
        self.utility_history_seller.append(seller_utility)
        self.temperature_history_buyer.append(buyer_temp)
        self.temperature_history_seller.append(seller_temp)
        self.acceptance_rates_over_time.append(accepted_count / max(total_proposals, 1))

    def get_utility_statistics(self, utilities):
        """Berechnet Statistiken für Utility-Verlauf"""
        if not utilities:
            return {}

        return {
            "min": min(utilities),
            "max": max(utilities),
            "mean": statistics.mean(utilities),
            "median": statistics.median(utilities),
            "std_dev": statistics.stdev(utilities) if len(utilities) > 1 else 0,
            "range": max(utilities) - min(utilities),
        }


def print_config_summary():
    """Zeigt Konfigurations-Übersicht"""
    if not DEBUG_CONFIG.get("SHOW_CONFIG_SUMMARY", False):
        return

    print("=" * 70)
    print("KONFIGURATIONS-ÜBERSICHT")
    print("=" * 70)
    print(f"Spieler: {SYSTEM_CONFIG['MAX_PLAYERS']}")
    print(f"Max Runden: {NEGOTIATION_CONFIG['MAX_ROUNDS']}")
    print(f"Start-Temperatur: {SA_CONFIG['INITIAL_TEMPERATURE']}")
    print(f"Min. Akzeptanzrate: {SA_CONFIG['MIN_ACCEPTANCE_RATE']}")
    print(f"Käufer: {BUYER_CONFIG['CLUB_NAME']}")
    print(f"Verkäufer: {SELLER_CONFIG['CLUB_NAME']}")
    print("=" * 70)


def analyze_team_composition(buyer_club, seller_club, squad):
    """Analysiert Team-Zusammensetzung"""
    if not ANALYSIS_CONFIG.get("ANALYZE_ATTRIBUTE_DISTRIBUTION", False):
        return

    print(f"\n{'-'*50}")
    print("TEAM-KOMPOSITION ANALYSE")
    print(f"{'-'*50}")

    # Analysiere Attribute
    key_attrs = ANALYSIS_CONFIG.get("KEY_ATTRIBUTES", [])

    for attr in key_attrs:
        values = []
        for idx in squad[:10]:  # Erste 10 Positionen
            player = buyer_club.players[idx]
            if hasattr(player, attr):
                values.append(getattr(player, attr))

        if values:
            avg_val = sum(values) / len(values)
            print(
                f"{attr.capitalize():>15}: Ø {avg_val:5.1f} (Range: {min(values)}-{max(values)})"
            )

    # Altersverteilung
    if ANALYSIS_CONFIG.get("ANALYZE_AGE_DISTRIBUTION", False):
        ages = [buyer_club.players[idx].age for idx in squad]
        age_groups = ANALYSIS_CONFIG.get("AGE_GROUPS", {})

        print(f"\nALTERSVERTEILUNG:")
        print(f"Durchschnitt: {sum(ages)/len(ages):.1f} Jahre")

        for group_name, (min_age, max_age) in age_groups.items():
            count = sum(1 for age in ages if min_age <= age <= max_age)
            percentage = count / len(ages) * 100
            print(
                f"{group_name:>10} ({min_age}-{max_age}): {count:2d} Spieler ({percentage:4.1f}%)"
            )


def analyze_position_preferences(buyer_club, seller_club, initial_squad, final_squad):
    """Analysiert Positions-Präferenzen"""
    if not ANALYSIS_CONFIG.get("ANALYZE_POSITION_PREFERENCES", False):
        return

    print(f"\n{'-'*50}")
    print("POSITIONS-PRÄFERENZ ANALYSE")
    print(f"{'-'*50}")

    num_pos = ANALYSIS_CONFIG.get("NUM_POSITIONS_TO_ANALYZE", 10)

    # Analysiere Veränderungen in ersten X Positionen
    print(f"Änderungen in ersten {num_pos} Positionen:")
    changes = 0
    for i in range(min(num_pos, len(final_squad))):
        if initial_squad[i] != final_squad[i]:
            changes += 1
            old_player = buyer_club.players[initial_squad[i]]
            new_player = buyer_club.players[final_squad[i]]
            print(f"  Pos {i:2d}: {old_player.name} → {new_player.name}")

    print(
        f"Gesamt: {changes}/{num_pos} Positionen geändert ({changes/num_pos*100:.1f}%)"
    )

    # Analysiere Präferenz für hohe vs niedrige Indizes
    high_indices = sum(1 for idx in final_squad[:num_pos] if idx >= 20)
    low_indices = sum(1 for idx in final_squad[:num_pos] if idx < 10)
    mid_indices = num_pos - high_indices - low_indices

    print(f"\nVerteilung in ersten {num_pos} Positionen:")
    print(f"Defensive (0-9):   {low_indices:2d} ({low_indices/num_pos*100:4.1f}%)")
    print(f"Mittelfeld (10-19): {mid_indices:2d} ({mid_indices/num_pos*100:4.1f}%)")
    print(f"Angriff (20-29):   {high_indices:2d} ({high_indices/num_pos*100:4.1f}%)")


def print_synergy_analysis(buyer_club, seller_club, squad):
    """Zeigt Synergieeffekt-Analyse"""
    if not ANALYSIS_CONFIG.get("CALCULATE_SYNERGY_STATS", False):
        return

    print(f"\n{'-'*50}")
    print("SYNERGIE-EFFEKTE ANALYSE")
    print(f"{'-'*50}")

    # Berechne Synergien separat
    total_synergy_buyer = buyer_club._calculate_synergy_bonus(squad)
    total_synergy_seller = seller_club._calculate_synergy_bonus(squad)

    print(f"Käufer Synergien:   {total_synergy_buyer:7.2f}")
    print(f"Verkäufer Synergien: {total_synergy_seller:7.2f}")

    # Analysiere Altersverteilung
    ages = [buyer_club.players[idx].age for idx in squad]
    age_bonus_buyer = buyer_club._calculate_age_bonus(squad)
    age_bonus_seller = seller_club._calculate_age_bonus(squad)

    print(f"\nAlters-Boni:")
    print(f"Käufer:   {age_bonus_buyer:7.2f}")
    print(f"Verkäufer: {age_bonus_seller:7.2f}")
    print(f"Ø Alter:  {sum(ages)/len(ages):7.1f} Jahre")


def print_extended_statistics(
    analyzer,
    buyer_club,
    seller_club,
    initial_squad,
    final_squad,
    start_time,
    accepted_swaps,
    max_rounds,
):
    """Zeigt erweiterte Statistiken am Ende"""
    if not LOGGING_CONFIG.get("SHOW_EXTENDED_STATS", False):
        return

    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "=" * 70)
    print("ERWEITERTE VERHANDLUNGS-STATISTIKEN")
    print("=" * 70)

    # Zeit-Statistiken
    print(f"ZEIT-STATISTIKEN:")
    print(f"Gesamtdauer:        {duration:8.2f} Sekunden")
    print(f"Runden/Sekunde:     {max_rounds/duration:8.2f}")
    print(f"Swaps/Sekunde:      {accepted_swaps/duration:8.2f}")
    print(f"Ø Zeit/Runde:       {duration/max_rounds*1000:8.2f} ms")

    # Utility-Entwicklung
    if analyzer.utility_history_buyer and LOGGING_CONFIG.get(
        "SHOW_UTILITY_DEVELOPMENT", False
    ):
        print(f"\nUTILITY-ENTWICKLUNG:")

        buyer_stats = analyzer.get_utility_statistics(analyzer.utility_history_buyer)
        seller_stats = analyzer.get_utility_statistics(analyzer.utility_history_seller)

        print(f"KÄUFER ({buyer_club.club_name}):")
        print(f"  Start:           {analyzer.utility_history_buyer[0]:10.2f}")
        print(f"  Ende:            {analyzer.utility_history_buyer[-1]:10.2f}")
        print(
            f"  Verbesserung:    {analyzer.utility_history_buyer[-1] - analyzer.utility_history_buyer[0]:10.2f}"
        )
        print(f"  Maximum:         {buyer_stats['max']:10.2f}")
        print(f"  Minimum:         {buyer_stats['min']:10.2f}")
        print(f"  Standardabw.:    {buyer_stats['std_dev']:10.2f}")

        print(f"\nVERKÄUFER ({seller_club.club_name}):")
        print(f"  Start:           {analyzer.utility_history_seller[0]:10.2f}")
        print(f"  Ende:            {analyzer.utility_history_seller[-1]:10.2f}")
        print(
            f"  Verbesserung:    {analyzer.utility_history_seller[-1] - analyzer.utility_history_seller[0]:10.2f}"
        )
        print(f"  Maximum:         {seller_stats['max']:10.2f}")
        print(f"  Minimum:         {seller_stats['min']:10.2f}")
        print(f"  Standardabw.:    {seller_stats['std_dev']:10.2f}")

    # Temperatur-Entwicklung
    if analyzer.temperature_history_buyer:
        print(f"\nTEMPERATUR-ENTWICKLUNG:")
        print(f"Käufer Start:       {analyzer.temperature_history_buyer[0]:8.2f}")
        print(f"Käufer Ende:        {analyzer.temperature_history_buyer[-1]:8.2f}")
        print(f"Verkäufer Start:    {analyzer.temperature_history_seller[0]:8.2f}")
        print(f"Verkäufer Ende:     {analyzer.temperature_history_seller[-1]:8.2f}")

    # Akzeptanzraten über Zeit
    if analyzer.acceptance_rates_over_time:
        print(f"\nAKZEPTANZRATEN:")
        rates = analyzer.acceptance_rates_over_time
        print(f"Start (erste 100):  {sum(rates[:100])/len(rates[:100])*100:6.2f}%")
        print(
            f"Mitte:             {sum(rates[len(rates)//3:2*len(rates)//3])/len(rates[len(rates)//3:2*len(rates)//3])*100:6.2f}%"
        )
        print(f"Ende (letzte 100):  {sum(rates[-100:])/len(rates[-100:])*100:6.2f}%")
        print(f"Gesamt:            {sum(rates)/len(rates)*100:6.2f}%")

    # Team-Komposition
    analyze_team_composition(buyer_club, seller_club, final_squad)

    # Positions-Präferenzen
    analyze_position_preferences(buyer_club, seller_club, initial_squad, final_squad)

    # Synergieeffekte
    print_synergy_analysis(buyer_club, seller_club, final_squad)


def run_football_negotiation(buyer_club, seller_club, mediator):
    """Führt eine Verhandlung mit erweiterten Statistiken durch"""

    max_rounds = NEGOTIATION_CONFIG["MAX_ROUNDS"]
    analyzer = NegotiationAnalyzer()
    start_time = time.time()

    # Initiale Spieler-Zuordnung
    current_squad = mediator.init_squads()
    initial_squad = current_squad.copy()

    print("=" * 70)
    print("SPIELER-VERHANDLUNG GESTARTET")
    print("=" * 70)
    print(f"Käufer: {buyer_club.club_name}")
    print(f"Verkäufer: {seller_club.club_name}")
    print(f"Anzahl Spieler: {len(current_squad)}")
    print(f"Max. Runden: {max_rounds:,}")
    print()

    print("Start-Lineup:", current_squad)
    print(f"Start-Utility {buyer_club.club_name}: ", end="")
    buyer_club.print_utility(current_squad)
    print(f", {seller_club.club_name}: ", end="")
    seller_club.print_utility(current_squad)
    print("\n")

    # Zeige detaillierte Start-Informationen
    if LOGGING_CONFIG.get("SHOW_DETAILED_START_INFO", False):
        print("BEISPIEL SPIELER:")
        num_examples = LOGGING_CONFIG.get("NUM_EXAMPLE_PLAYERS", 5)
        for i in range(min(num_examples, len(buyer_club.players))):
            player = buyer_club.players[i]
            buyer_rating = buyer_club.evaluate_player(player)
            seller_rating = seller_club.evaluate_player(player)
            print(
                f"  {i:2d}: {player.name:<25} | Käufer: {buyer_rating:6.1f} | Verkäufer: {seller_rating:6.1f}"
            )
        print()

    accepted_swaps = 0
    last_progress_round = 0

    # Hauptschleife
    for round_num in range(max_rounds):
        # Wähle Art des Vorschlags basierend auf Konfiguration
        shuffle_freq = NEGOTIATION_CONFIG.get("TEAM_SHUFFLE_FREQUENCY", 0.01)
        if round_num % round(1 / shuffle_freq) == 0:
            shuffle_pct = NEGOTIATION_CONFIG.get("SHUFFLE_PERCENTAGE", 0.2)
            proposal = mediator.propose_team_shuffle(current_squad, shuffle_pct)
        else:
            proposal = mediator.propose_player_swap(current_squad)

        # Beide Vereine abstimmen lassen
        buyer_vote = buyer_club.vote(current_squad, proposal)
        seller_vote = seller_club.vote(current_squad, proposal)

        # Swap wird nur akzeptiert, wenn beide Vereine zustimmen
        if buyer_vote and seller_vote:
            current_squad = proposal
            accepted_swaps += 1

            # Protokolliere für Analyse
            buyer_utility = buyer_club.evaluate_squad(current_squad)
            seller_utility = seller_club.evaluate_squad(current_squad)
            analyzer.record_swap(
                round_num,
                current_squad,
                buyer_utility,
                seller_utility,
                buyer_club.t,
                seller_club.t,
                accepted_swaps,
                round_num + 1,
            )

            # Fortschritt basierend auf Konfiguration
            swap_interval = NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_SWAPS", 250)
            if accepted_swaps % swap_interval == 0 or accepted_swaps == 1:
                print(f"\n{'-'*50}")
                print(f"Runde {round_num:,}, Akzeptierte Swaps: {accepted_swaps:,}")
                print(f"{'-'*50}")
                print(f"Squad: {current_squad[:10]}...")
                print(f"Utility {buyer_club.club_name}: ", end="")
                buyer_club.print_utility(current_squad)
                print(f", {seller_club.club_name}: ", end="")
                seller_club.print_utility(current_squad)
                print()

                # Temperatur-Info
                if LOGGING_CONFIG.get("SHOW_TEMPERATURE_UPDATES", False):
                    print(
                        f"Temperaturen: Käufer={buyer_club.t:.2f}, Verkäufer={seller_club.t:.2f}"
                    )

                # Beispiel-Wechsel
                num_changes = LOGGING_CONFIG.get("NUM_EXAMPLE_CHANGES", 3)
                changed_positions = [
                    i for i in range(len(current_squad)) if current_squad[i] != i
                ][:num_changes]
                if changed_positions:
                    print("Beispiel Wechsel:")
                    for pos in changed_positions:
                        player = buyer_club.players[current_squad[pos]]
                        print(f"  Pos {pos:2d}: {player.name} ({player.club})")

                last_progress_round = round_num

        # Zeige Fortschritt alle X Runden (falls wenige Swaps)
        round_interval = NEGOTIATION_CONFIG.get("PROGRESS_INTERVAL_ROUNDS", 2000)
        if round_num % round_interval == 0 and round_num > last_progress_round:
            acceptance_rate = accepted_swaps / (round_num + 1) * 100
            print(
                f"Runde {round_num:,}: {accepted_swaps:,} Swaps (~{acceptance_rate:.1f}%)"
            )

    # Finale Analyse und Ausgabe
    print("\n" + "=" * 70)
    print("VERHANDLUNGS-ENDERGEBNIS")
    print("=" * 70)
    print(f"Finaler Squad: {current_squad}")
    print(f"\nEnd-Utility {buyer_club.club_name}: ", end="")
    buyer_club.print_utility(current_squad)
    print(f", {seller_club.club_name}: ", end="")
    seller_club.print_utility(current_squad)
    print(f"\n\nBASIS-STATISTIKEN:")
    print(f"- Akzeptierte Swaps: {accepted_swaps:,} von {max_rounds:,}")
    print(f"- Akzeptanzrate: {accepted_swaps/max_rounds*100:.2f}%")

    # Zeige erweiterte Statistiken
    print_extended_statistics(
        analyzer,
        buyer_club,
        seller_club,
        initial_squad,
        current_squad,
        start_time,
        accepted_swaps,
        max_rounds,
    )


def main():
    """Hauptfunktion mit Konfiguration"""
    print("=" * 70)
    print("FUßBALL-VERHANDLUNGSSYSTEM")
    print("=" * 70)
    print("Konfiguration: config.py")
    print("Alle Parameter vollständig anpassbar!")
    print()

    # Zeige Konfigurations-Übersicht
    print_config_summary()

    # Lade Spielerdaten basierend auf Konfiguration
    print("Lade Spielerdaten...")
    csv_file = SYSTEM_CONFIG["CSV_FILE_PATH"]
    max_players = SYSTEM_CONFIG["MAX_PLAYERS"]

    try:
        players = PlayerDataLoader.load_from_csv(csv_file, max_players=max_players)
        print(f"CSV erfolgreich geladen: {csv_file}")
    except:
        if SYSTEM_CONFIG.get("AUTO_CREATE_SAMPLE_DATA", True):
            print("Erstelle automatisch Beispieldaten...")
            players = PlayerDataLoader._create_sample_players(max_players)
        else:
            print("❌ Keine Spielerdaten verfügbar!")
            return

    print(f"Geladen: {len(players)} Spieler\n")

    # Erstelle Vereine basierend auf Konfiguration
    print("Erstelle Vereine...")
    buyer_club = BuyerClubAgent(BUYER_CONFIG["CLUB_NAME"])
    seller_club = SellerClubAgent(SELLER_CONFIG["CLUB_NAME"])

    # Setze Spielerdaten
    buyer_club.set_players(players)
    seller_club.set_players(players)

    # Zeige Vereins-Info
    print(f"- {buyer_club.club_name}: Offensive & Technik (GEHEIM)")
    print(f"- {seller_club.club_name}: Defensive & Vielseitigkeit (GEHEIM)")
    print(f"- Käufer bevorzugt späte Positionen (Angriff)")
    print(f"- Verkäufer bevorzugt frühe Positionen (Defense)")

    # Erstelle Mediator
    print("\nErstelle Mediator...")
    mediator = FootballMediator(
        buyer_club.get_contract_size(), seller_club.get_contract_size()
    )

    # Validiere Konfiguration
    if DEBUG_CONFIG.get("VALIDATE_CONFIG", True):
        print("✅ Konfiguration validiert")

    # Starte Verhandlung
    print("\nStarte Verhandlung...\n")
    run_football_negotiation(buyer_club, seller_club, mediator)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        if DEBUG_CONFIG.get("DEBUG_MODE", False):
            import traceback

            traceback.print_exc()
