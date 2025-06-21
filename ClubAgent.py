# ClubAgent.py - Generische Vereinsklasse für echte Vereine
import math
import random
from typing import List, Dict, Optional
from PlayerAgent import FootballAgent, Player

# Sichere config imports
try:
    from config import SA_CONFIG, UTILITY_CONFIG, LOGGING_CONFIG, STRATEGY_CONFIG
except ImportError:
    # Fallback-Werte
    SA_CONFIG = {
        "INITIAL_TEMPERATURE": 50.0,
        "MIN_ACCEPTANCE_RATE": 0.8,
        "MAX_ITERATIONS": 10000,
        "CALIBRATION_ITERATIONS": 1000,
        "MIN_TEMPERATURE": 0.01,
        "FALLBACK_TEMPERATURE": 10.0,
        "MIN_CALIBRATION_RATE": 0.1,
    }
    UTILITY_CONFIG = {
        "SYNERGY_WEIGHT": 10.0,
        "AGE_BONUS_WEIGHT": 1.0,
        "IDEAL_AVERAGE_AGE": 27,
        "AGE_PENALTY_PER_YEAR": 2.0,
        "MAX_AGE_BONUS": 100.0,
        "SAME_CLUB_SYNERGY": 20.0,
        "SAME_COUNTRY_SYNERGY": 10.0,
        "CHEMISTRY_THRESHOLD": 10,
        "VALUE_WEIGHT": 0.1,
    }
    LOGGING_CONFIG = {
        "SHOW_TEMPERATURE_CALIBRATION": True,
    }
    STRATEGY_CONFIG = {
        "offensive": {"ATTRIBUTE_MULTIPLIERS": {}},
        "defensive": {"ATTRIBUTE_MULTIPLIERS": {}},
        "balanced": {"ATTRIBUTE_MULTIPLIERS": {}},
        "technical": {"ATTRIBUTE_MULTIPLIERS": {}},
    }


class ClubAgent(FootballAgent):
    """
    Generischer Verein-Agent, der für jeden echten Verein verwendet werden kann
    """
    
    def __init__(self, club_name: str, strategy: str = "balanced", custom_weights: Dict[str, float] = None):
        """
        Args:
            club_name: Name des echten Vereins aus der CSV
            strategy: Spielstrategie ("offensive", "defensive", "balanced", "technical", "custom")
            custom_weights: Benutzerdefinierte Attribut-Gewichtungen (nur bei strategy="custom")
        """
        self.strategy = strategy  # WICHTIG: Zuerst strategy setzen!
        self.custom_weights = custom_weights
        super().__init__(club_name)  # Dann erst super() aufrufen
        self.original_players = []  # Ursprüngliche Spieler des Vereins
        
        # SA-Parameter aus Konfiguration
        self.t = SA_CONFIG["INITIAL_TEMPERATURE"]
        self.mind_ac_rate = SA_CONFIG["MIN_ACCEPTANCE_RATE"]
        self.max_iter = SA_CONFIG["MAX_ITERATIONS"]
        self.max_sim = SA_CONFIG["CALIBRATION_ITERATIONS"]
        
    def set_original_players(self, players: List[Player]):
        """Setzt die ursprünglichen Spieler des Vereins"""
        self.original_players = players.copy()
        self.set_players(players)
        
    def _init_attribute_weights(self) -> List[float]:
        """
        Initialisiert Gewichtungen basierend auf der Strategie oder benutzerdefinierten Werten
        """
        # Attribut-Reihenfolge (muss mit Player.get_attribute_vector() übereinstimmen)
        attribute_order = [
            "ball_control", "dribbling", "slide_tackle", "stand_tackle",
            "aggression", "reactions", "att_position", "interceptions",
            "vision", "composure", "crossing", "short_pass", "long_pass",
            "acceleration", "stamina", "strength", "balance", "sprint_speed",
            "agility", "jumping", "heading", "shot_power", "finishing", "long_shots"
        ]
        
        # Bei benutzerdefinierten Gewichtungen
        if self.strategy == "custom" and self.custom_weights:
            weights = [self.custom_weights.get(attr, 1.0) for attr in attribute_order]
            max_weight = max(weights) if weights else 1.0
            return [w / max_weight for w in weights]
        
        # Basis-Gewichtungen
        weights_dict = {
            "ball_control": 1.5,
            "dribbling": 1.5,
            "slide_tackle": 1.5,
            "stand_tackle": 1.5,
            "aggression": 1.0,
            "reactions": 1.5,
            "att_position": 1.5,
            "interceptions": 1.5,
            "vision": 1.5,
            "composure": 1.5,
            "crossing": 1.2,
            "short_pass": 1.5,
            "long_pass": 1.3,
            "acceleration": 1.5,
            "stamina": 1.8,
            "strength": 1.5,
            "balance": 1.5,
            "sprint_speed": 1.5,
            "agility": 1.5,
            "jumping": 1.3,
            "heading": 1.3,
            "shot_power": 1.5,
            "finishing": 1.5,
            "long_shots": 1.3,
        }
        
        # Modifiziere basierend auf Strategie
        if self.strategy in STRATEGY_CONFIG:
            strategy_multipliers = STRATEGY_CONFIG[self.strategy].get("ATTRIBUTE_MULTIPLIERS", {})
            for attr, multiplier in strategy_multipliers.items():
                if attr in weights_dict:
                    weights_dict[attr] *= multiplier
                
        # Konvertiere zu Liste
        weights = [weights_dict.get(attr, 1.0) for attr in attribute_order]
        max_weight = max(weights) if weights else 1.0
        return [w / max_weight for w in weights]
    
    def _init_position_weights(self) -> List[float]:
        """
        Positions-Gewichtungen basierend auf Strategie
        """
        # Basis: Gleiche Gewichtung für alle Positionen
        weights = [1.0] * 30
        
        # Modifiziere basierend auf Positions-Präferenz der Strategie
        if self.strategy in STRATEGY_CONFIG:
            position_pref = STRATEGY_CONFIG[self.strategy].get("POSITION_PREFERENCE", "ANY")
            
            if position_pref == "ATT":
                # Höhere Gewichtung für offensive Positionen
                for i in range(20, 30):
                    weights[i] = 1.5
            elif position_pref == "DEF":
                # Höhere Gewichtung für defensive Positionen
                for i in range(0, 10):
                    weights[i] = 1.5
            elif position_pref == "MID":
                # Höhere Gewichtung für Mittelfeld-Positionen
                for i in range(10, 20):
                    weights[i] = 1.5
                
        return weights
    
    def vote(self, current_squad: List[int], proposed_squad: List[int]) -> bool:
        """Entscheidet über Transfer mit Simulated Annealing"""
        current_utility = self.evaluate_squad(current_squad)
        proposed_utility = self.evaluate_squad(proposed_squad)
        
        self.cur_iter += 1
        
        # Temperaturkalibrierung
        if self.cur_iter == self.max_sim:
            self.avg_delta = self.sum_delta / self.anz_delta if self.anz_delta > 0 else 1.0
            vb_rate = (self.max_sim - self.anz_delta) / self.max_sim
            akzeptanzrate = max(SA_CONFIG["MIN_CALIBRATION_RATE"], self.mind_ac_rate - vb_rate)
            
            if self.avg_delta > 0 and akzeptanzrate > 0:
                self.t = -self.avg_delta / math.log(akzeptanzrate)
            else:
                self.t = SA_CONFIG["FALLBACK_TEMPERATURE"]
                
            self.delta_t = self.t / (self.max_iter - self.max_sim)
            
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
                    try:
                        akz_wk = math.exp(-delta / self.t)
                        return random.random() <= akz_wk
                    except OverflowError:
                        return False
                else:
                    return False
                    
    def _calculate_synergy_bonus(self, squad_indices: List[int]) -> float:
        """Berechnet Synergieeffekte zwischen Spielern"""
        synergy = 0.0
        
        for i in range(len(squad_indices) - 1):
            if squad_indices[i] >= len(self.players) or squad_indices[i+1] >= len(self.players):
                continue
                
            player1 = self.players[squad_indices[i]]
            player2 = self.players[squad_indices[i + 1]]
            
            # Bonus für Spieler vom gleichen Original-Verein
            club1 = getattr(player1, 'club', '')
            club2 = getattr(player2, 'club', '')
            if club1 == club2 and club1 == self.club_name:
                synergy += UTILITY_CONFIG.get("SAME_CLUB_SYNERGY", 20)
                
            # Bonus für Spieler aus gleichem Land
            country1 = getattr(player1, 'country', '')
            country2 = getattr(player2, 'country', '')
            if country1 == country2 and country1:
                synergy += UTILITY_CONFIG.get("SAME_COUNTRY_SYNERGY", 10)
                
            # Pass-Synergie
            pass1 = getattr(player1, 'short_pass', 0)
            pass2 = getattr(player2, 'short_pass', 0)
            pass_diff = abs(pass1 - pass2)
            chemistry_threshold = UTILITY_CONFIG.get("CHEMISTRY_THRESHOLD", 10)
            if pass_diff < chemistry_threshold:
                synergy += (chemistry_threshold - pass_diff)
            
        return synergy * UTILITY_CONFIG.get("SYNERGY_WEIGHT", 5.0)
    
    def _calculate_age_bonus(self, squad_indices: List[int]) -> float:
        """Berechnet Altersbonus basierend auf Strategie"""
        ages = []
        for idx in squad_indices:
            if idx < len(self.players):
                age = getattr(self.players[idx], 'age', 25)
                ages.append(age)
                
        if not ages:
            return 0.0
            
        avg_age = sum(ages) / len(ages)
        
        # Strategie-spezifische Alters-Präferenz
        age_pref = "balanced"
        if self.strategy in STRATEGY_CONFIG:
            age_pref = STRATEGY_CONFIG[self.strategy].get("AGE_PREFERENCE", "balanced")
        
        ideal_age = UTILITY_CONFIG.get("IDEAL_AVERAGE_AGE", 26)
        if age_pref == "young":
            ideal_age = 24
        elif age_pref == "experienced":
            ideal_age = 29
            
        age_penalty = abs(avg_age - ideal_age) * UTILITY_CONFIG.get("AGE_PENALTY_PER_YEAR", 3.0)
        max_bonus = UTILITY_CONFIG.get("MAX_AGE_BONUS", 50.0)
        
        return max(0, max_bonus - age_penalty)
    
    def evaluate_squad(self, squad_indices: List[int]) -> float:
        """
        Erweiterte Squad-Bewertung mit zusätzlichen Faktoren
        """
        # Basis-Bewertung von der Elternklasse
        base_utility = super().evaluate_squad(squad_indices)
        
        # Zusätzlicher Bonus für Original-Spieler
        original_player_bonus = 0
        for idx in squad_indices:
            if idx < len(self.players):
                player = self.players[idx]
                player_club = getattr(player, 'club', '')
                if player_club == self.club_name:
                    original_player_bonus += 10  # Loyalitäts-Bonus
                    
        # Wert-Integration
        total_value = 0
        for idx in squad_indices:
            if idx < len(self.players):
                value = getattr(self.players[idx], 'value', 0)
                total_value += value
        value_bonus = (total_value / 1_000_000) * UTILITY_CONFIG.get("VALUE_WEIGHT", 0.1)
        
        return base_utility + original_player_bonus + value_bonus