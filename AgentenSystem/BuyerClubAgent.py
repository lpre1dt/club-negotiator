import math
import random
from typing import List
from PlayerAgent import FootballAgent, Player
from config import BUYER_CONFIG, SA_CONFIG, UTILITY_CONFIG, LOGGING_CONFIG


class BuyerClubAgent(FootballAgent):
    """
    Käufer-Verein: Konfigurierbar über config.py
    Geheime Strategie: Bevorzugt technische und offensive Spieler
    """

    def __init__(self, club_name: str = None):
        # Verwende Namen aus Konfiguration falls nicht anderweitig angegeben
        if club_name is None:
            club_name = BUYER_CONFIG["CLUB_NAME"]
        super().__init__(club_name)

        # Überschreibe SA-Parameter mit Konfigurationswerten
        self.t = SA_CONFIG["INITIAL_TEMPERATURE"]
        self.mind_ac_rate = SA_CONFIG["MIN_ACCEPTANCE_RATE"]
        self.max_iter = SA_CONFIG["MAX_ITERATIONS"]
        self.max_sim = SA_CONFIG["CALIBRATION_ITERATIONS"]

    def _init_attribute_weights(self) -> List[float]:
        """
        Lädt Gewichtungen aus der Konfigurationsdatei
        """
        weights_dict = BUYER_CONFIG["ATTRIBUTE_WEIGHTS"]

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
        return BUYER_CONFIG["POSITION_WEIGHTS"].copy()

    def vote(self, current_squad: List[int], proposed_squad: List[int]) -> bool:
        """
        Käufer-Entscheidung mit konfigurierbarem Simulated Annealing
        """
        current_utility = self.evaluate_squad(current_squad)
        proposed_utility = self.evaluate_squad(proposed_squad)

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
