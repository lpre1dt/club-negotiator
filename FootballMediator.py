# FootballMediator.py
import random
from typing import List


class FootballMediator:
    """
    Mediator für Fußballspieler-Verhandlungen zwischen Vereinen
    Koordiniert Spieler-Tausch-Vorschläge
    """

    def __init__(self, num_players_a: int, num_players_b: int):
        """
        Initialisiert den Mediator

        Args:
            num_players_a: Anzahl Spieler des ersten Vereins
            num_players_b: Anzahl Spieler des zweiten Vereins

        Raises:
            ValueError: wenn die Anzahl der Spieler nicht übereinstimmt
        """
        if num_players_a != num_players_b:
            raise ValueError(
                f"Verhandlung nicht möglich: Verschiedene Spieleranzahl "
                f"({num_players_a} vs {num_players_b})"
            )
        self.num_players = num_players_a

    def init_squads(self) -> List[int]:
        """
        Erstellt eine initiale Spieler-Zuordnung

        Returns:
            List[int]: Sortierte Liste von Spieler-Indices
        """
        return list(range(self.num_players))

    def propose_player_swap(self, current_squad: List[int]) -> List[int]:
        """
        Schlägt einen Spielertausch vor (2-opt move)

        Args:
            current_squad: aktuelle Spieler-Zuordnung

        Returns:
            List[int]: neuer Vorschlag mit getauschten Spielern
        """
        proposed_squad = current_squad.copy()

        if len(proposed_squad) > 1:
            # Zwei zufällige Spieler auswählen und deren Positionen tauschen
            pos1 = random.randint(0, len(proposed_squad) - 1)
            pos2 = random.randint(0, len(proposed_squad) - 1)

            # Sicherstellen, dass verschiedene Positionen gewählt werden
            while pos1 == pos2 and len(proposed_squad) > 1:
                pos2 = random.randint(0, len(proposed_squad) - 1)

            # Spieler tauschen
            proposed_squad[pos1], proposed_squad[pos2] = (
                proposed_squad[pos2],
                proposed_squad[pos1],
            )

        return proposed_squad

    def propose_team_shuffle(
        self, current_squad: List[int], shuffle_percentage: float = 0.3
    ) -> List[int]:
        """
        Schlägt eine stärkere Umstellung des Teams vor

        Args:
            current_squad: aktuelle Spieler-Zuordnung
            shuffle_percentage: Anteil der Spieler, die umgestellt werden

        Returns:
            List[int]: neuer Vorschlag mit umgestelltem Team
        """
        proposed_squad = current_squad.copy()
        num_to_shuffle = max(1, int(len(proposed_squad) * shuffle_percentage))

        # Zufällige Indizes zum Umstellen auswählen
        indices_to_shuffle = random.sample(range(len(proposed_squad)), num_to_shuffle)

        # Werte an diesen Positionen mischen
        values_to_shuffle = [proposed_squad[i] for i in indices_to_shuffle]
        random.shuffle(values_to_shuffle)

        # Zurück in das Array einsetzen
        for i, val in zip(indices_to_shuffle, values_to_shuffle):
            proposed_squad[i] = val

        return proposed_squad