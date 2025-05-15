from abc import ABC, abstractmethod
from typing import List, Dict
import math


class Player:
    """
    Repräsentiert einen Fußballspieler mit seinen Attributen
    """

    def __init__(self, name: str, data: Dict):
        self.name = name
        self.country = data.get("country", "")
        self.age = int(data.get("age", 0))
        self.club = data.get("club", "")
        self.value = self._parse_value(data.get("value", "$0"))

        # Fußball-Attribute (0-100 Skala)
        self.ball_control = int(data.get("ball_control", 0))
        self.dribbling = int(data.get("dribbling", 0))
        self.slide_tackle = int(data.get("slide_tackle", 0))
        self.stand_tackle = int(data.get("stand_tackle", 0))
        self.aggression = int(data.get("aggression", 0))
        self.reactions = int(data.get("reactions", 0))
        self.att_position = int(data.get("att_position", 0))
        self.interceptions = int(data.get("interceptions", 0))
        self.vision = int(data.get("vision", 0))
        self.composure = int(data.get("composure", 0))
        self.crossing = int(data.get("crossing", 0))
        self.short_pass = int(data.get("short_pass", 0))
        self.long_pass = int(data.get("long_pass", 0))
        self.acceleration = int(data.get("acceleration", 0))
        self.stamina = int(data.get("stamina", 0))
        self.strength = int(data.get("strength", 0))
        self.balance = int(data.get("balance", 0))
        self.sprint_speed = int(data.get("sprint_speed", 0))
        self.agility = int(data.get("agility", 0))
        self.jumping = int(data.get("jumping", 0))
        self.heading = int(data.get("heading", 0))
        self.shot_power = int(data.get("shot_power", 0))
        self.finishing = int(data.get("finishing", 0))
        self.long_shots = int(data.get("long_shots", 0))

    def _parse_value(self, value_str: str) -> float:
        """Parst den Marktwert aus String zu Float (in Dollar)"""
        if not value_str or value_str == "$0":
            return 0.0

        # Entferne $ und andere Zeichen
        clean_value = value_str.replace("$", "").replace(",", "")

        # Handle Million/Thousand suffixes
        if ".000" in clean_value:
            return float(clean_value.replace(".000", "")) * 1000
        elif ".00" in clean_value:
            return float(clean_value.replace(".00", ""))
        else:
            return float(clean_value)

    def get_attribute_vector(self) -> List[float]:
        """Gibt alle Spielerattribute als Vektor zurück"""
        return [
            self.ball_control,
            self.dribbling,
            self.slide_tackle,
            self.stand_tackle,
            self.aggression,
            self.reactions,
            self.att_position,
            self.interceptions,
            self.vision,
            self.composure,
            self.crossing,
            self.short_pass,
            self.long_pass,
            self.acceleration,
            self.stamina,
            self.strength,
            self.balance,
            self.sprint_speed,
            self.agility,
            self.jumping,
            self.heading,
            self.shot_power,
            self.finishing,
            self.long_shots,
        ]

    def __str__(self):
        return f"{self.name} ({self.club}, {self.age} Jahre, ${self.value:,.0f})"


class FootballAgent(ABC):
    """
    Abstrakte Basisklasse für Fußball-Agenten (Vereine)
    """

    def __init__(self, club_name: str):
        self.club_name = club_name
        self.players = []

        # Geheime Gewichtungsmatrix für Spielerattribute
        self.attribute_weights = self._init_attribute_weights()

        # Positions-Gewichtungen (GEHEIM!)
        self.position_weights = self._init_position_weights()

        # Simulated Annealing Parameter
        self.t = 50.0
        self.delta_t = 0.0
        self.mind_ac_rate = 0.8
        self.max_iter = 10000
        self.cur_iter = 0
        self.max_sim = 1000
        self.sum_delta = 0.0
        self.anz_delta = 0
        self.avg_delta = 0.0

    @abstractmethod
    def _init_attribute_weights(self) -> List[float]:
        """Initialisiert die geheimen Gewichtungen für Spielerattribute"""
        pass

    @abstractmethod
    def _init_position_weights(self) -> List[float]:
        """Initialisiert die geheimen Gewichtungen für Positionen im Team"""
        pass

    def set_players(self, players: List[Player]):
        """Setzt die verfügbaren Spieler"""
        self.players = players

    def evaluate_player(self, player: Player) -> float:
        """
        Bewertet einen Spieler basierend auf den geheimen Gewichtungen
        DIESE FUNKTION IST GEHEIM - andere Agenten kennen sie nicht!
        """
        attributes = player.get_attribute_vector()
        score = sum(w * a for w, a in zip(self.attribute_weights, attributes))
        return score

    def evaluate_squad(self, squad_indices: List[int]) -> float:
        """
        Bewertet ein Team mit POSITIONS-ABHÄNGIGER Utility
        DIESE FUNKTION IST GEHEIM - andere Agenten kennen sie nicht!
        """
        total_utility = 0.0

        # Basis-Utility: Gewichtete Summe der Spieler
        for i, idx in enumerate(squad_indices):
            player = self.players[idx]
            player_utility = self.evaluate_player(player)

            # Position-basierte Gewichtung
            position_weight = self.position_weights[
                min(i, len(self.position_weights) - 1)
            ]

            total_utility += player_utility * position_weight

        # BONUS: Synergieeffekte zwischen benachbarten Spielern
        synergy_bonus = self._calculate_synergy_bonus(squad_indices)
        total_utility += synergy_bonus

        # BONUS: Altersverteilung
        age_bonus = self._calculate_age_bonus(squad_indices)
        total_utility += age_bonus

        return total_utility

    def _calculate_synergy_bonus(self, squad_indices: List[int]) -> float:
        """Berechnet Synergieeffekte zwischen Spielern"""
        synergy = 0.0

        for i in range(len(squad_indices) - 1):
            player1 = self.players[squad_indices[i]]
            player2 = self.players[squad_indices[i + 1]]

            # Beispiel: Spieler mit ähnlichen Pass-Werten ergänzen sich gut
            pass_synergy = abs(player1.short_pass - player2.short_pass)
            synergy += max(0, 10 - pass_synergy)  # Bonus für ähnliche Pass-Werte

            # Beispiel: Verschiedene Altersgruppen ergänzen sich
            age_diff = abs(player1.age - player2.age)
            synergy += max(
                0, 5 - age_diff / 3
            )  # Bonus für ausgewogene Altersverteilung

        return synergy * 10  # Verstärke den Effekt

    def _calculate_age_bonus(self, squad_indices: List[int]) -> float:
        """Berechnet Bonus für ausgewogene Altersverteilung"""
        ages = [self.players[idx].age for idx in squad_indices]
        avg_age = sum(ages) / len(ages)

        # Bonus für Durchschnittsalter zwischen 25-29
        ideal_age = 27
        age_penalty = abs(avg_age - ideal_age) * 2

        return max(0, 100 - age_penalty)

    @abstractmethod
    def vote(self, current_squad: List[int], proposed_squad: List[int]) -> bool:
        """Entscheidet über Annahme eines Spieler-Tausch-Vorschlags"""
        pass

    def print_utility(self, squad_indices: List[int]):
        """Gibt die Utility des Teams aus"""
        utility = self.evaluate_squad(squad_indices)
        print(f"{utility:.2f}", end="")

    def get_contract_size(self) -> int:
        """Gibt die Anzahl der verfügbaren Spieler zurück"""
        return len(self.players)
