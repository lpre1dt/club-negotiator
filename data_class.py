# data_class.py - Erweiterte Hilfsfunktionen für Datenverarbeitung

def get_name():
    """Gibt den Standard-Dateinamen zurück"""
    return "player_stats.csv"


def fix_mojibake(text):
    """
    Behebt Mojibake (falsch kodierte Zeichen) in Texten
    
    Args:
        text: String mit potentiellen Encoding-Problemen
        
    Returns:
        Korrigierter String
    """
    if not isinstance(text, str):
        return text
        
    try:
        # Versuche latin1 -> utf-8 Konvertierung
        return text.encode('latin1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        try:
            # Fallback: Windows-1252 -> utf-8
            return text.encode('windows-1252').decode('utf-8')
        except:
            # Wenn alles fehlschlägt, gib Original zurück
            return text


def clean_value_string(value_str):
    """
    Bereinigt Währungsstrings und konvertiert zu float
    
    Args:
        value_str: String wie "$1.5M" oder "€45K"
        
    Returns:
        float: Numerischer Wert
    """
    if not value_str or value_str in ['0', 'N/A', 'Unknown']:
        return 0.0
        
    # Entferne Währungssymbole
    value_str = value_str.replace('$', '').replace('€', '').replace('£', '')
    value_str = value_str.replace(',', '').strip()
    
    # Handle Millionen/Tausend Suffixe
    multiplier = 1
    if value_str.endswith('M'):
        multiplier = 1_000_000
        value_str = value_str[:-1]
    elif value_str.endswith('K'):
        multiplier = 1_000
        value_str = value_str[:-1]
    
    try:
        return float(value_str) * multiplier
    except ValueError:
        return 0.0


def normalize_club_names(club_name):
    """
    Normalisiert Vereinsnamen für konsistente Vergleiche
    
    Args:
        club_name: Original Vereinsname
        
    Returns:
        Normalisierter Vereinsname
    """
    if not club_name:
        return "Unknown"
        
    # Entferne führende/nachfolgende Leerzeichen
    club_name = club_name.strip()
    
    # Korrigiere häufige Inkonsistenzen
    replacements = {
        'FC ': '',
        ' FC': '',
        'CF ': '',
        ' CF': '',
        'United': 'Utd',
        'City': 'City',
        'Real ': 'Real ',
        'Atletico': 'Atlético',
        'Munich': 'München',
    }
    
    for old, new in replacements.items():
        club_name = club_name.replace(old, new)
        
    return club_name


def get_position_from_attributes(player_attributes):
    """
    Bestimmt die wahrscheinlichste Position eines Spielers basierend auf Attributen
    
    Args:
        player_attributes: Dictionary mit Spielerattributen
        
    Returns:
        str: Position (GK, DEF, MID, ATT)
    """
    # Torwart-Check
    gk_attrs = ['gk_positioning', 'gk_diving', 'gk_handling', 'gk_kicking', 'gk_reflexes']
    gk_score = sum(int(player_attributes.get(attr, 0)) for attr in gk_attrs)
    
    if gk_score > 200:  # Wahrscheinlich ein Torwart
        return "GK"
    
    # Feldspieler-Positionen
    defensive_score = (
        int(player_attributes.get('slide_tackle', 0)) +
        int(player_attributes.get('stand_tackle', 0)) +
        int(player_attributes.get('interceptions', 0)) +
        int(player_attributes.get('heading', 0))
    )
    
    midfield_score = (
        int(player_attributes.get('vision', 0)) +
        int(player_attributes.get('short_pass', 0)) +
        int(player_attributes.get('long_pass', 0)) +
        int(player_attributes.get('stamina', 0))
    )
    
    attacking_score = (
        int(player_attributes.get('finishing', 0)) +
        int(player_attributes.get('shot_power', 0)) +
        int(player_attributes.get('att_position', 0)) +
        int(player_attributes.get('dribbling', 0))
    )
    
    scores = {
        'DEF': defensive_score,
        'MID': midfield_score,
        'ATT': attacking_score
    }
    
    return max(scores, key=scores.get)


def calculate_player_overall(player_attributes, position=None):
    """
    Berechnet einen Gesamtwert für einen Spieler
    
    Args:
        player_attributes: Dictionary mit Spielerattributen
        position: Position des Spielers (optional)
        
    Returns:
        float: Gesamtwert (0-100)
    """
    if not position:
        position = get_position_from_attributes(player_attributes)
    
    # Positions-spezifische Gewichtungen
    weights = {
        'GK': {
            'gk_positioning': 0.2, 'gk_diving': 0.2, 'gk_handling': 0.2,
            'gk_kicking': 0.1, 'gk_reflexes': 0.2, 'reactions': 0.1
        },
        'DEF': {
            'slide_tackle': 0.15, 'stand_tackle': 0.15, 'interceptions': 0.15,
            'heading': 0.1, 'strength': 0.1, 'stamina': 0.1,
            'short_pass': 0.1, 'reactions': 0.05, 'composure': 0.05, 'balance': 0.05
        },
        'MID': {
            'vision': 0.15, 'short_pass': 0.15, 'long_pass': 0.1,
            'stamina': 0.15, 'ball_control': 0.1, 'dribbling': 0.1,
            'reactions': 0.1, 'composure': 0.05, 'agility': 0.05, 'balance': 0.05
        },
        'ATT': {
            'finishing': 0.2, 'shot_power': 0.15, 'att_position': 0.15,
            'dribbling': 0.1, 'ball_control': 0.1, 'acceleration': 0.1,
            'sprint_speed': 0.05, 'agility': 0.05, 'reactions': 0.05, 'composure': 0.05
        }
    }
    
    position_weights = weights.get(position, weights['MID'])
    
    overall = 0
    for attr, weight in position_weights.items():
        value = int(player_attributes.get(attr, 0))
        overall += value * weight
        
    return min(100, overall)  # Cap bei 100


def filter_valid_players(players_data):
    """
    Filtert ungültige Spielerdaten heraus
    
    Args:
        players_data: Liste von Spieler-Dictionaries
        
    Returns:
        Liste von validen Spielern
    """
    valid_players = []
    
    for player in players_data:
        # Check für minimale erforderliche Attribute
        if not player.get('player') or player.get('player') == 'Unknown':
            continue
            
        # Check ob genug Attribute vorhanden sind
        required_attrs = ['ball_control', 'dribbling', 'finishing', 'stamina']
        has_attrs = all(player.get(attr) and int(player.get(attr, 0)) > 0 
                       for attr in required_attrs)
        
        if has_attrs:
            valid_players.append(player)
            
    return valid_players


def get_transfer_value_estimation(player_attributes, age=None):
    """
    Schätzt den Transferwert eines Spielers
    
    Args:
        player_attributes: Dictionary mit Spielerattributen
        age: Alter des Spielers
        
    Returns:
        float: Geschätzter Transferwert
    """
    # Basis-Wert basierend auf Overall
    overall = calculate_player_overall(player_attributes)
    base_value = (overall / 100) ** 2 * 100_000_000  # Exponentiell für Top-Spieler
    
    # Alters-Modifikator
    if age:
        age = int(age)
        if age < 24:
            age_modifier = 1.2  # Junge Spieler sind wertvoller
        elif age < 28:
            age_modifier = 1.0  # Prime age
        elif age < 32:
            age_modifier = 0.8
        else:
            age_modifier = 0.5
    else:
        age_modifier = 1.0
        
    return base_value * age_modifier


# Export wichtiger Funktionen für andere Module
__all__ = [
    'get_name',
    'fix_mojibake',
    'clean_value_string',
    'normalize_club_names',
    'get_position_from_attributes',
    'calculate_player_overall',
    'filter_valid_players',
    'get_transfer_value_estimation'
]