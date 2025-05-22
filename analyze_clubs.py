import csv
from collections import Counter

# Configuration from the main system (relevant parts)
CSV_FILE_PATH = "player_stats.csv"
CSV_ENCODING = "latin1" # As determined previously
MIN_PLAYERS_THRESHOLD = 11
TOP_N_CLUBS = 30

def analyze_player_counts_and_get_top_30():
    club_player_counts = Counter()
    
    try:
        with open(CSV_FILE_PATH, "r", encoding=CSV_ENCODING) as file:
            reader = csv.DictReader(file, delimiter=';')
            if not reader.fieldnames or 'club' not in reader.fieldnames:
                print("ERROR: CSV header issue or 'club' column missing.")
                return

            for row in reader:
                club_name = row.get('club')
                if club_name and club_name.strip():
                    club_player_counts[club_name.strip()] += 1
                    
    except FileNotFoundError:
        print(f"ERROR: CSV file not found at {CSV_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while reading the CSV: {e}")
        return

    eligible_clubs = {club: count for club, count in club_player_counts.items() if count >= MIN_PLAYERS_THRESHOLD}
    
    # Sort by player count (descending) then by club name (ascending)
    sorted_eligible_clubs = sorted(eligible_clubs.items(), key=lambda item: (-item[1], item[0]))
    
    top_clubs_to_report = sorted_eligible_clubs[:TOP_N_CLUBS]
    
    print(f"Top {TOP_N_CLUBS} clubs with {MIN_PLAYERS_THRESHOLD} or more players:")
    print("==================================================")
    if top_clubs_to_report:
        for club, count in top_clubs_to_report:
            # Ensure club names are printable, handle potential encoding issues for display if necessary
            try:
                printable_club_name = club
            except Exception:
                printable_club_name = club.encode('ascii', 'replace').decode('ascii') # Fallback
            print(f"{printable_club_name} ({count} players)")
    else:
        print(f"No clubs found meeting the criteria to select top {TOP_N_CLUBS}.")
    print("==================================================")
    print("Analysis for top clubs complete.")

if __name__ == "__main__":
    analyze_player_counts_and_get_top_30()
