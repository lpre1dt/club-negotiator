import math
import random
from typing import List, Dict, Optional # Optional und Dict hinzugefügt
from PlayerAgent import FootballAgent, Player
from config import CLUB_CONFIG, SELLER_CONFIG, SA_CONFIG, UTILITY_CONFIG, LOGGING_CONFIG # CLUB_CONFIG hinzugefügt


class SellerClubAgent(FootballAgent):
    """
    Repräsentiert einen Verkäufer-Club-Agenten im Fußball-Verhandlungssystem.

    Diese Klasse erbt von `FootballAgent` und implementiert die spezifische Logik und
    Strategie für einen Verkäufer-Club. Die Konfiguration des Agenten (z.B. Attribut-
    und Positionsgewichtungen, Simulated-Annealing-Parameter) erfolgt primär über
    die `SELLER_CONFIG` und `SA_CONFIG` aus der zentralen Konfigurationsdatei (`config.py`).
    Die Strategie des Verkäufers ist typischerweise darauf ausgerichtet, defensivstarke
    und vielseitige Spieler zu halten oder einen guten Preis für sie zu erzielen.

    Attribute:
        attribute_weights_dict (Dict[str, float]): Ein Dictionary, das die Roh-Gewichtungen
            für Spielerattribute enthält, entweder aus der Konfiguration oder als Override.
    """

    def __init__(self, club_name: str = None, attribute_weights_override: Optional[Dict[str, float]] = None):
        """
        Initialisiert den SellerClubAgent.

        Args:
            club_name (str, optional): Der Name des Clubs. Wenn None, wird der Name aus
                `SELLER_CONFIG` oder `CLUB_CONFIG` geladen.
            attribute_weights_override (Optional[Dict[str, float]], optional): Ein Dictionary,
                das verwendet werden kann, um die Attributgewichtungen zur Laufzeit zu überschreiben.
                Wenn None, werden die Gewichtungen aus `SELLER_CONFIG` verwendet.
        """
        # Bestimme den zu verwendenden Club-Namen.
        # Priorität: 1. Übergebener club_name, 2. SELLER_CONFIG["CLUB_NAME"], 3. CLUB_CONFIG["SELLER_CLUB_NAME"]
        resolved_club_name = club_name
        if resolved_club_name is None:
            resolved_club_name = SELLER_CONFIG.get("CLUB_NAME") # Versuche spezifische Verkäufer-Club-Benennung
            if resolved_club_name is None: # Falls nicht in SELLER_CONFIG gesetzt
                 resolved_club_name = CLUB_CONFIG.get("SELLER_CLUB_NAME", "Standard Verkäufer Club") # Fallback

        super().__init__(resolved_club_name) # Rufe Konstruktor der Basisklasse auf.

        # Speichere die Quelle der Attributgewichtungen (Override oder Standardkonfiguration).
        if attribute_weights_override is not None:
            self.attribute_weights_dict: Dict[str, float] = attribute_weights_override
            # Optional: Logging der Verwendung von überschriebenen Gewichten.
            # print(f"[{self.club_name}] Verwendet überschriebene Attributgewichtungen.")
        else:
            self.attribute_weights_dict: Dict[str, float] = SELLER_CONFIG["ATTRIBUTE_WEIGHTS"]
            # Optional: Logging der Verwendung von Standardgewichten.
            # print(f"[{self.club_name}] Verwendet Standard-Attributgewichtungen aus SELLER_CONFIG.")

        # Initialisiere die normalisierte `self.attribute_weights`-Liste erneut.
        self.attribute_weights = self._init_attribute_weights()
        
        # Setze spezifische Simulated Annealing (SA) Parameter aus der Konfiguration.
        self.t = SA_CONFIG.get("INITIAL_TEMPERATURE", 50.0) # Standardwert falls nicht in Config
        self.mind_ac_rate = SA_CONFIG["MIN_ACCEPTANCE_RATE"]
        self.max_iter = SA_CONFIG["MAX_ITERATIONS"]
        self.max_sim = SA_CONFIG["CALIBRATION_ITERATIONS"]

    def _init_attribute_weights(self) -> List[float]:
        """
        Lädt Gewichtungen aus der Konfigurationsdatei (oder verwendet das Override-Dict).
        Uses self.attribute_weights_dict which is set in __init__.
        """
        weights_dict = self.attribute_weights_dict # Use the stored dictionary

        # Konvertiere Dictionary zu Liste in korrekter Reihenfolge
        attribute_order = [
            "ball_control",
            "dribbling",
            "slide_tackle",
            "stand_tackle",
            "aggression",
            "reactions",
            "att_position",
            "interceptions",
            "vision",
            "composure",
            "crossing",
            "short_pass",
            "long_pass",
            "acceleration",
            "stamina",
            "strength",
            "balance",
            "sprint_speed",
            "agility",
            "jumping",
            "heading",
            "shot_power",
            "finishing",
            "long_shots",
        ]

        weights = [weights_dict.get(attr, 1.0) for attr in attribute_order]

        # Normalisierung der Gewichte
        max_weight = max(weights)
        return [w / max_weight for w in weights]

    def _init_position_weights(self) -> List[float]:
        """
        Lädt Positions-Gewichtungen aus der Konfiguration
        """
        return SELLER_CONFIG["POSITION_WEIGHTS"].copy()

    def vote(self, player_to_give: Player, player_to_receive: Player) -> bool:
        """
        Verkäufer-Entscheidung für einen Inter-Club Spieler-Tausch mit konfigurierbarem Simulated Annealing.
        Bewertet den Tausch basierend auf der Änderung der Team-Utility.
        """
        # Current utility of the agent's actual squad
        current_utility = self.calculate_utility_for_hypothetical_squad(self.players)

        # Create a hypothetical squad list after the trade
        hypothetical_squad_players = self.players.copy()
        
        player_to_give_index = self.get_player_index(player_to_give)

        if player_to_give_index is None:
            print(f"⚠️ [{self.club_name}] Spieler zum Abgeben ({player_to_give.name}) nicht im eigenen Kader gefunden. Tausch abgelehnt.")
            return False # Reject if the player to give isn't found

        # Remove player_to_give and add player_to_receive
        del hypothetical_squad_players[player_to_give_index]
        hypothetical_squad_players.append(player_to_receive)
        
        proposed_utility = self.calculate_utility_for_hypothetical_squad(hypothetical_squad_players)

        self.cur_iter += 1

        # Temperaturkalibrierung
        if self.cur_iter == self.max_sim:
            self.avg_delta = (
                self.sum_delta / self.anz_delta if self.anz_delta > 0 else 1.0
            )
            vb_rate = (self.max_sim - self.anz_delta) / self.max_sim
            akzeptanzrate = max(
                SA_CONFIG["MIN_CALIBRATION_RATE"], self.mind_ac_rate - vb_rate
            )

            # Verbesserte Temperaturberechnung mit Fallback
            if self.avg_delta > 0:
                self.t = -self.avg_delta / math.log(akzeptanzrate)
            else:
                self.t = SA_CONFIG["FALLBACK_TEMPERATURE"]

            self.delta_t = self.t / (self.max_iter - self.max_sim)

            # Zeige Kalibrierung je nach Konfiguration
            if LOGGING_CONFIG.get("SHOW_TEMPERATURE_CALIBRATION", True):
                print(
                    f"[{self.club_name}] Temperatur kalibriert: T={self.t:.2f}, AvgDelta={self.avg_delta:.2f}"
                )

        elif self.cur_iter > self.max_sim:
            self.t -= self.delta_t
            self.t = max(self.t, SA_CONFIG["MIN_TEMPERATURE"])

        # Simulated Annealing Entscheidung
        if proposed_utility > current_utility:
            return True
        else:
            delta = current_utility - proposed_utility
            self.sum_delta += delta
            self.anz_delta += 1

            if self.cur_iter < self.max_sim:
                return random.random() <= self.mind_ac_rate
            else:
                if self.t > 0:
                    akz_wk = math.exp(-delta / self.t)
                    return random.random() <= akz_wk
                else:
                    return False

    def _calculate_synergy_bonus(self, squad_indices: List[int]) -> float:
        """
        Berechnet Synergieeffekte mit konfigurierbaren Parametern
        """
        synergy = 0.0
        max_pass_synergy = UTILITY_CONFIG.get("MAX_PASS_SYNERGY", 10.0)
        pass_threshold = UTILITY_CONFIG.get("PASS_SYNERGY_THRESHOLD", 10.0)
        max_age_synergy = UTILITY_CONFIG.get("MAX_AGE_SYNERGY", 5.0)
        age_divisor = UTILITY_CONFIG.get("AGE_SYNERGY_DIVISOR", 3.0)

        for i in range(len(squad_indices) - 1):
            player1 = self.players[squad_indices[i]]
            player2 = self.players[squad_indices[i + 1]]

            # Pass-Synergie
            pass_synergy = abs(player1.short_pass - player2.short_pass)
            synergy += max(
                0, max_pass_synergy - pass_synergy / pass_threshold * max_pass_synergy
            )

            # Alters-Synergie
            age_diff = abs(player1.age - player2.age)
            synergy += max(0, max_age_synergy - age_diff / age_divisor)

        synergy_weight = UTILITY_CONFIG.get("SYNERGY_WEIGHT", 10.0)
        return synergy * synergy_weight

    def _calculate_age_bonus(self, squad_indices: List[int]) -> float:
        """
        Berechnet Altersbonus mit konfigurierbaren Parametern
        """
        ages = [self.players[idx].age for idx in squad_indices]
        avg_age = sum(ages) / len(ages)

        ideal_age = UTILITY_CONFIG.get("IDEAL_AVERAGE_AGE", 27)
        penalty_per_year = UTILITY_CONFIG.get("AGE_PENALTY_PER_YEAR", 2.0)
        max_bonus = UTILITY_CONFIG.get("MAX_AGE_BONUS", 100.0)

        age_penalty = abs(avg_age - ideal_age) * penalty_per_year
        bonus = max(0, max_bonus - age_penalty)

        age_weight = UTILITY_CONFIG.get("AGE_BONUS_WEIGHT", 1.0)
        return bonus * age_weight
