from abc import ABC, abstractmethod
from typing import List, Dict, Optional # Added Optional
import math


class Player:
    """
    Repräsentiert einen Fußballspieler mit all seinen Attributen und Eigenschaften.

    Diese Klasse dient als Datencontainer für einzelne Spieler, inklusive persönlicher Daten,
    Vereinszugehörigkeit, Marktwert und einer umfassenden Liste von spielrelevanten Attributen,
    die typischerweise auf einer Skala von 0-100 bewertet werden.
    """

    def __init__(self, name: str, data: Dict[str, any]):
        """
        Initialisiert ein neues Spieler-Objekt.

        Args:
            name (str): Der Name des Spielers.
            data (Dict[str, any]): Ein Dictionary, das die Rohdaten des Spielers enthält.
                                   Fehlende Werte werden durch Standardwerte ersetzt.
        """
        self.name: str = name
        self.country: str = data.get("country", "Unbekannt")
        self.age: int = int(data.get("age", 0))
        self.club: str = data.get("club", "Unbekannt")
        # Der Marktwert wird durch eine separate Methode geparst und als Float gespeichert.
        self.value: float = self._parse_value(data.get("value", "$0"))

        # Fußballspezifische Attribute (typischerweise auf einer Skala von 0-100)
        # Für jedes Attribut wird ein Standardwert von 0 gesetzt, falls es nicht in data vorhanden ist.
        self.ball_control: int = int(data.get("ball_control", 0))
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
        self.long_shots: int = int(data.get("long_shots", 0))

    def _parse_value(self, value_str: str) -> float:
        """
        Parst den Marktwert eines Spielers von einem String (z.B. "$5.500.000" oder "$500K")
        in einen numerischen Float-Wert (Dollar).

        Args:
            value_str (str): Der Marktwert als String.

        Returns:
            float: Der numerische Marktwert. Gibt 0.0 zurück, wenn der String ungültig oder "$0" ist.
        """
        if not value_str or value_str.strip() == "$0": # .strip() hinzugefügt für mehr Robustheit
            return 0.0

        # Entferne Währungssymbole und Tausendertrennzeichen.
        # Beachtet sowohl '.' als auch ',' als mögliche Tausendertrennzeichen.
        clean_value_str = value_str.replace("$", "").replace("€", "").replace(",", "").replace("£", "") # Robuster für verschiedene Währungen
        
        multiplier = 1.0
        if 'M' in clean_value_str.upper(): # Millionen
            multiplier = 1_000_000
            clean_value_str = clean_value_str.upper().replace("M", "")
        elif 'K' in clean_value_str.upper(): # Tausende
            multiplier = 1_000
            clean_value_str = clean_value_str.upper().replace("K", "")
        elif ".000" in clean_value_str: # Format wie "5.500.000" -> "5.500" * 1000 (falls . als Tausender)
             # This specific case needs careful handling if '.' is decimal or thousands separator
             # Assuming for now that if ".000" is present, it implies thousands for large numbers not millions
             # This part might need adjustment based on actual data patterns for values not ending in K or M.
             # The original logic:
             # if ".000" in clean_value: return float(clean_value.replace(".000", "")) * 1000
             # This is ambiguous if clean_value is "5.500.000". Does it become 5.5 * 1000 or 5500 * 1000?
             # Let's assume it means the value is already in base units if no K/M, but the .000 is just for display.
             # The original logic was likely trying to handle values like "€10.000" as 10000.
             # And "€1.500.000" as 1500000.
             # A common European notation.
             # If the value is something like "1.500.000", replacing ".000" would leave "1.500", then float("1.500") -> 1.5 * 1000 = 1500. This is wrong.
             # It should be 1500000.
             # Let's refine: if only dots exist, they are likely thousand separators.
             if '.' in clean_value_str and 'M' not in value_str.upper() and 'K' not in value_str.upper():
                 # Example: "1.500.000" or "500.000"
                 clean_value_str = clean_value_str.replace('.', '')


        try:
            return float(clean_value_str) * multiplier
        except ValueError:
            # Fallback, falls die Konvertierung fehlschlägt
            # print(f"Warnung: Konnte Marktwert '{value_str}' nicht parsen. Setze auf 0.0.") # Optional: Logging
            return 0.0

    def get_attribute_vector(self) -> List[int]: # Geändert zu List[int], da Attribute als int gespeichert sind
        """
        Gibt eine Liste aller spielrelevanten numerischen Attribute des Spielers zurück.
        Die Reihenfolge der Attribute ist fest definiert und wichtig für konsistente Berechnungen.

        Returns:
            List[int]: Eine Liste der Integer-Werte der Spielerattribute.
        """
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

    def __str__(self) -> str:
        """
        Gibt eine benutzerfreundliche String-Repräsentation des Spielers zurück.

        Returns:
            str: Formatierter String mit Name, Club, Alter und Marktwert des Spielers.
        """
        return f"{self.name} ({self.club}, {self.age} Jahre, Wert: ${self.value:,.0f})"


class FootballAgent(ABC):
    """
    Abstrakte Basisklasse für einen Fußball-Agenten (Verein).

    Diese Klasse definiert die grundlegende Struktur und Funktionalität eines Agenten,
    der in Spieler-Verhandlungen teilnimmt. Sie beinhaltet Methoden zur Spielerbewertung,
    Kader-Management und Entscheidungsfindung mittels Simulated Annealing.
    Spezifische Strategien und Gewichtungen werden in abgeleiteten Klassen implementiert.

    Attribute:
        club_name (str): Name des Vereins, den der Agent repräsentiert.
        players (List[Player]): Liste der Spieler-Objekte, die dem Kader des Agenten angehören.
        attribute_weights (List[float]): Normalisierte Gewichtungen für Spielerattribute.
        position_weights (List[float]): Gewichtungen für Kaderpositionen.
        t (float): Aktuelle Temperatur für Simulated Annealing.
        delta_t (float): Änderungsrate der Temperatur pro Iteration.
        mind_ac_rate (float): Mindestakzeptanzrate während der SA-Kalibrierung.
        max_iter (int): Maximale Anzahl an Iterationen für den SA-Prozess.
        cur_iter (int): Aktuelle Iterationsnummer im SA-Prozess.
        max_sim (int): Anzahl der Iterationen für die SA-Temperaturkalibrierung.
        sum_delta (float): Summe der Utility-Differenzen für die SA-Kalibrierung.
        anz_delta (int): Anzahl der negativen Utility-Differenzen für die SA-Kalibrierung.
        avg_delta (float): Durchschnittliche negative Utility-Differenz für die SA-Kalibrierung.
    """

    def __init__(self, club_name: str):
        """
        Initialisiert einen neuen Fußball-Agenten.

        Args:
            club_name (str): Der Name des Vereins.
        """
        self.club_name: str = club_name
        self.players: List[Player] = []  # Kader des Agenten

        # Initialisiere die geheimen Gewichtungen durch Aufruf der abstrakten Methoden.
        # Diese müssen in den Subklassen implementiert werden.
        # Hinweis: self.attribute_weights_dict wird in Subklassen vor _init_attribute_weights() gesetzt.
        self.attribute_weights: List[float] = self._init_attribute_weights() 
        self.position_weights: List[float] = self._init_position_weights()

        # Initialisierung der Parameter für Simulated Annealing (SA)
        # Diese können in Subklassen oder durch Konfigurationen angepasst werden.
        self.t = 50.0
        self.delta_t = 0.0
        self.mind_ac_rate = 0.8
        self.max_iter = 10000
        self.cur_iter = 0
        self.max_sim = 1000
        self.sum_delta = 0.0
        self.anz_delta = 0
        self.avg_delta = 0.0

    def get_player_index(self, player_to_find: Player) -> Optional[int]:
        """
        Finds the index of a given Player object in the agent's current player list.

        Args:
            player_to_find: The Player object to find.

        Returns:
            The index of the player if found, otherwise None.
        """
        for i, player in enumerate(self.players):
            # Comparing by object identity first, then by name as a fallback.
            # This assumes player_to_find might be a different instance with the same data.
            if player is player_to_find or player.name == player_to_find.name:
                return i
        return None

    def calculate_utility_for_hypothetical_squad(self, hypothetical_players_list: List[Player]) -> float:
        """
        Calculates the squad utility for a given list of Player objects.
        This method is used for evaluating hypothetical trades without altering self.players.
        """
        total_utility = 0.0
        squad_indices = list(range(len(hypothetical_players_list))) # Indices for this hypothetical list

        # Basis-Utility: Gewichtete Summe der Spieler
        for i, player_object_in_hypothetical_list in enumerate(hypothetical_players_list):
            # evaluate_player works on a Player object directly, doesn't need an index from self.players
            player_utility = self.evaluate_player(player_object_in_hypothetical_list)

            # Position-basierte Gewichtung
            # min() ensures we don't go out of bounds if hypothetical_players_list is shorter/longer
            # than the defined position_weights.
            position_weight = self.position_weights[
                min(i, len(self.position_weights) - 1)
            ]
            total_utility += player_utility * position_weight

        # For synergy and age bonus, we need to adapt them to work with List[Player]
        # instead of List[int] (indices into self.players)

        # BONUS: Synergieeffekte zwischen benachbarten Spielern
        # Temporarily set self.players to the hypothetical list for bonus calculations
        original_players = self.players
        self.players = hypothetical_players_list
        try:
            # Note: _calculate_synergy_bonus and _calculate_age_bonus expect squad_indices
            # that refer to the *current* self.players. So we use the generated squad_indices.
            synergy_bonus = self._calculate_synergy_bonus(squad_indices)
            total_utility += synergy_bonus

            # BONUS: Altersverteilung
            age_bonus = self._calculate_age_bonus(squad_indices)
            total_utility += age_bonus
        finally:
            # Restore original self.players
            self.players = original_players
            
        return total_utility

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
        if not squad_indices: # Check if the list of indices is empty
            return 0.0
        
        ages = [self.players[idx].age for idx in squad_indices]
        if not ages: # Should not happen if squad_indices is not empty, but as a safeguard
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
