import sys
import csv

# Add the AgentenSystem directory to the Python path
sys.path.insert(0, "./AgentenSystem")

from main import load_club_data_with_validation, create_club_agents_with_data
from config import SYSTEM_CONFIG, CLUB_CONFIG, BUYER_CONFIG, SELLER_CONFIG, validate_club_config, DISPLAY_CONFIG

def run_test_script():
    print("--- Starting test script ---")

    # Call load_club_data_with_validation()
    print("\n--- Calling load_club_data_with_validation() ---")
    try:
        (buyer_players, seller_players), (buyer_name, seller_name) = load_club_data_with_validation()
        
        print("\n--- Output from load_club_data_with_validation() ---")
        print(f"Buyer Club Name: {buyer_name}")
        print(f"Number of Buyer Players: {len(buyer_players)}")
        print(f"Seller Club Name: {seller_name}")
        print(f"Number of Seller Players: {len(seller_players)}")

        # Check for non-zero player counts
        if len(buyer_players) == 0:
            print("WARNING: Buyer players list is empty.")
        else:
            print(f"SUCCESS: Buyer players list for {buyer_name} is populated with {len(buyer_players)} players.")

        if len(seller_players) == 0:
            print("WARNING: Seller players list is empty.")
        else:
            print(f"SUCCESS: Seller players list for {seller_name} is populated with {len(seller_players)} players.")


        # Call create_club_agents_with_data()
        print("\n--- Calling create_club_agents_with_data() ---")
        # Ensure DISPLAY_CONFIG settings are True to get output from create_club_agents_with_data
        DISPLAY_CONFIG["SHOW_DETAILED_START_INFO"] = True # Already True by default, but good to be explicit

        if buyer_players and seller_players: # Only call if players were loaded
            create_club_agents_with_data(buyer_players, seller_players, buyer_name, seller_name)
        else:
            print("Skipping create_club_agents_with_data() due to empty player list(s).")

    except Exception as e:
        print(f"An error occurred during test script execution: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- End of test script ---")

if __name__ == "__main__":
    print("--- Validating Club Configuration (initial) ---")
    validate_club_config()
    
    # Update club names in config directly for the test
    CLUB_CONFIG["BUYER_CLUB_NAME"] = "FC Porto"
    CLUB_CONFIG["SELLER_CLUB_NAME"] = "FC Bayern München" # This is the target name
    
    # Ensure BUYER_CONFIG and SELLER_CONFIG use these names if they are set to None
    if BUYER_CONFIG["CLUB_NAME"] is None: 
        BUYER_CONFIG["CLUB_NAME"] = CLUB_CONFIG["BUYER_CLUB_NAME"]
    if SELLER_CONFIG["CLUB_NAME"] is None:
        SELLER_CONFIG["CLUB_NAME"] = CLUB_CONFIG["SELLER_CLUB_NAME"]
    
    print(f"Updated CLUB_CONFIG for test: Buyer='{CLUB_CONFIG['BUYER_CLUB_NAME']}', Seller='{CLUB_CONFIG['SELLER_CLUB_NAME']}'")

    # Run the main test script
    run_test_script()
