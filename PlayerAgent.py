# PlayerAgent.py
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
        # Weitere Fußball-Attribute
        self.curve = int(data.get("curve", 0))
        self.fk_acc = int(data.get("fk_acc", 0))
        self.penalties = int(data.get("penalties", 0))
        self.volleys = int(data.get("volleys", 0))
        
        # Torwart-Attribute (meist 0 für Feldspieler)
        self.gk_positioning = int(data.get("gk_positioning", 0))
        self.gk_diving = int(data.get("gk_diving", 0))
        self.gk_handling = int(data.get("gk_handling", 0))
        self.gk_kicking = int(data.get("gk_kicking", 0))
        self.gk_reflexes = int(data.get("gk_reflexes", 0))

    def _parse_value(self, value_str: str) -> float:
        """Parst den Marktwert aus String zu Float (in Dollar)"""
        if not value_str or value_str == "$0":
            return 0.0

        try:
            # Entferne $ und andere Zeichen
            clean_value = str(value_str).replace("$", "").replace(",", "").replace("€", "").strip()

            # Handle Million/Thousand suffixes
            if ".000" in clean_value:
                return float(clean_value.replace(".000", "")) * 1000
            elif ".00" in clean_value:
                return float(clean_value.replace(".00", ""))
            elif "M" in clean_value.upper():
                return float(clean_value.upper().replace("M", "")) * 1_000_000
            elif "K" in clean_value.upper():
                return float(clean_value.upper().replace("K", "")) * 1_000
            else:
                return float(clean_value)
        except (ValueError, TypeError):
            return 0.0

    def get_attribute_vector(self) -> List[float]:
        """Gibt alle Spielerattribute als Vektor zurück"""
        # Verwende getattr mit Standardwert 0 für fehlende Attribute
        return [
            getattr(self, 'ball_control', 0),
            getattr(self, 'dribbling', 0),
            getattr(self, 'slide_tackle', 0),
            getattr(self, 'stand_tackle', 0),
            getattr(self, 'aggression', 0),
            getattr(self, 'reactions', 0),
            getattr(self, 'att_position', 0),
            getattr(self, 'interceptions', 0),
            getattr(self, 'vision', 0),
            getattr(self, 'composure', 0),
            getattr(self, 'crossing', 0),
            getattr(self, 'short_pass', 0),
            getattr(self, 'long_pass', 0),
            getattr(self, 'acceleration', 0),
            getattr(self, 'stamina', 0),
            getattr(self, 'strength', 0),
            getattr(self, 'balance', 0),
            getattr(self, 'sprint_speed', 0),
            getattr(self, 'agility', 0),
            getattr(self, 'jumping', 0),
            getattr(self, 'heading', 0),
            getattr(self, 'shot_power', 0),
            getattr(self, 'finishing', 0),
            getattr(self, 'long_shots', 0),
        ]

    def __str__(self):
        try:
            value_str = f"${self.value:,.0f}" if self.value else "$0"
            return f"{self.name} ({self.club}, {self.age} Jahre, {value_str})"
        except:
            return f"{self.name}"


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
            if idx >= len(self.players):
                continue
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
            if squad_indices[i] >= len(self.players) or squad_indices[i+1] >= len(self.players):
                continue
                
            player1 = self.players[squad_indices[i]]
            player2 = self.players[squad_indices[i + 1]]

            # Beispiel: Spieler mit ähnlichen Pass-Werten ergänzen sich gut
            pass1 = getattr(player1, 'short_pass', 0)
            pass2 = getattr(player2, 'short_pass', 0)
            pass_synergy = abs(pass1 - pass2)
            synergy += max(0, 10 - pass_synergy)  # Bonus für ähnliche Pass-Werte

            # Beispiel: Verschiedene Altersgruppen ergänzen sich
            age1 = getattr(player1, 'age', 25)
            age2 = getattr(player2, 'age', 25)
            age_diff = abs(age1 - age2)
            synergy += max(
                0, 5 - age_diff / 3
            )  # Bonus für ausgewogene Altersverteilung

        return synergy * 10  # Verstärke den Effekt

    def _calculate_age_bonus(self, squad_indices: List[int]) -> float:
        """Berechnet Bonus für ausgewogene Altersverteilung"""
        ages = []
        for idx in squad_indices:
            if idx < len(self.players):
                age = getattr(self.players[idx], 'age', 25)
                ages.append(age)
                
        if not ages:
            return 0.0
            
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