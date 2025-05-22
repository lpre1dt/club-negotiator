"""
Streamlit Web-Anwendung für das Fußball-Verhandlungssystem.

Diese Anwendung bietet eine Benutzeroberfläche zur Interaktion mit dem 
Fußball-Verhandlungssystem. Sie ermöglicht Benutzern:
- Die Rohdaten der Spieler einzusehen ("Start").
- Vereine für eine Beispielanalyse auszuwählen und deren aggregierte Attribute zu vergleichen ("Vereinswahl").
- (Platzhalter) Detailliertere Analysen durchzuführen ("Analyse").
- Die Attributgewichtungen für Käufer- und Verkäufer-Agenten zu konfigurieren und
  eine Verhandlungssimulation zu starten ("Negotiation Configuration").
- Die Ergebnisse der durchgeführten Verhandlung zu visualisieren ("Negotiation Results").

Die Anwendung nutzt Streamlit für die UI-Komponenten und Pandas für die Datenmanipulation.
Matplotlib wird für die Erstellung von Diagrammen verwendet. Die Logik des Verhandlungssystems
wird aus dem `AgentenSystem`-Paket importiert. Daten und Konfigurationen werden über
`st.session_state` zwischen den Seiten und Durchläufen erhalten.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_class import fix_mojibake # Hilfsfunktion zur Korrektur von Mojibake-Zeichen.

# Stil für Matplotlib-Diagramme setzen, um ein konsistentes Aussehen zu gewährleisten.
plt.style.use('ggplot')

# Importiere Systemkonfigurationen und Klassen aus dem AgentenSystem-Paket.
import sys
sys.path.append('AgentenSystem') # Füge das AgentenSystem-Verzeichnis zum Python-Pfad hinzu.
from config import (
    CLUB_CONFIG, BUYER_CONFIG, SELLER_CONFIG, 
    NEGOTIATION_CONFIG, LOGGING_CONFIG, DISPLAY_CONFIG
)
from PlayerDataLoader import ClubBasedPlayerDataLoader
from BuyerClubAgent import BuyerClubAgent
from SellerClubAgent import SellerClubAgent
from FootballMediator import ClubBasedFootballMediator
from PlayerAgent import Player # Ensure Player is available for type hinting if needed elsewhere or for clarity
import time # For negotiation duration
import copy # For deep copying configurations

# Hauptnavigation der Anwendung: Auswahl der anzuzeigenden Seite.
page = st.selectbox(
    "Seite wählen", 
    ["Start", "Vereinswahl", "Analyse", "Negotiation Configuration", "Negotiation Results"],
    help="Wählen Sie hier die gewünschte Seite oder Funktion der Anwendung aus."
)

# Globale Datenvorbereitung: Einlesen und Bereinigen der Spielerdaten-CSV.
# Dieser Schritt wird einmal beim Start der App oder bei Bedarf ausgeführt.
@st.cache_data # Cache die geladenen und bereinigten Daten, um wiederholtes Laden zu vermeiden.
def load_and_clean_data(file_path: str, encoding: str) -> pd.DataFrame:
    """
    Lädt Spielerdaten aus einer CSV-Datei und bereinigt Textspalten von Mojibake-Zeichen.
    
    Args:
        file_path (str): Pfad zur CSV-Datei.
        encoding (str): Zeichenkodierung der CSV-Datei.
        
    Returns:
        pd.DataFrame: Das geladene und bereinigte DataFrame.
        
    Raises:
        Exception: Wenn das Laden oder die initiale Verarbeitung der Datei fehlschlägt.
    """
    df_loaded = pd.read_csv(file_path, encoding=encoding)
    for col in df_loaded.select_dtypes(include='object').columns:
        df_loaded[col] = df_loaded[col].apply(fix_mojibake)
    return df_loaded

try:
    # Lade die Haupt-Spielerdaten. Der Pfad und das Encoding könnten auch aus SYSTEM_CONFIG stammen.
    df = load_and_clean_data("player_stats.csv", encoding="latin1")
except Exception as e:
    st.error(f"Kritischer Fehler beim Laden der Spielerdaten-Datei: {e}")
    st.caption("Stellen Sie sicher, dass die Datei 'player_stats.csv' im Hauptverzeichnis vorhanden und lesbar ist.")
    st.stop() # Stoppt die Ausführung der App, wenn die Basisdaten nicht geladen werden können.

# ==============================================================================
# SEITE: Startseite - Anzeige der Rohdaten
# ==============================================================================
if page == "Start":
    st.title("Spieler-Rohdaten Übersicht")
    st.markdown("""
    Willkommen beim Fußball-Verhandlungssystem! Diese Seite zeigt die geladenen Rohdaten aller Spieler
    aus der `player_stats.csv`. Sie können die Tabelle durchsuchen und sortieren, um einen
    ersten Eindruck von den verfügbaren Spielerattributen zu erhalten.
    """)
    st.dataframe(df)
    st.caption(f"Insgesamt {len(df)} Spielerdatensätze geladen.")

# ==============================================================================
# SEITE: Vereinswahl - Vergleich von zwei Vereinen
# ==============================================================================
elif page == "Vereinswahl":
    st.title("Vereinsvergleich")
    st.markdown("""
    Wählen Sie zwei Vereine aus der Liste aus, um deren Spielerattribute aggregiert
    (als Summe oder Durchschnitt) zu vergleichen. Dies dient einer ersten explorativen Analyse.
    """)
    df_club = df[["player", "club"]]

    # Clubs extrahieren
    clubs = sorted(df["club"].dropna().unique())
    if len(clubs) < 2:
        st.warning("Nicht genug Clubs in den Daten.")
    else:
        club1 = st.selectbox("Club 1", clubs, index=0)
        club2 = st.selectbox("Club 2", clubs, index=1)

        # Aggregation auswählen
        aggregation = st.radio("Aggregation", ["Total", "Durchschnitt"])

        # Quantifizierbare Spalten
        non_numeric = ["player", "country", "club"]
        quant_cols = [col for col in df.columns if col not in non_numeric and pd.api.types.is_numeric_dtype(df[col])]

        # Welche Attribute anzeigen
        selected_cols = st.multiselect(
            "Welche Attribute vergleichen?",
            options=quant_cols,
            default=["acceleration", "stamina", "strength", "shot_power", "finishing"]
        )

        # Daten filtern
        filtered = df[df["club"].isin([club1, club2])]

        # Aggregieren
        if aggregation == "Total":
            agg_df = filtered.groupby("club")[selected_cols].sum()
        else:
            agg_df = filtered.groupby("club")[selected_cols].mean()

        # Chart anzeigen
        st.subheader("Visualisierung")
        fig, ax = plt.subplots(figsize=(10, 6))
        agg_df[selected_cols].T.plot(kind="bar", ax=ax)
        ax.set_title(f"{aggregation} Vergleich: {club1} vs. {club2}")
        ax.set_xlabel("Attribut")
        ax.set_ylabel("Wert")
        ax.legend(title="Club")
        st.pyplot(fig)

        # Tabelle anzeigen
        st.subheader("Tabelle der aggregierten Werte")
        st.dataframe(agg_df[selected_cols].style.format("{:.2f}"))

# ---------------- Seite: Analyse (Platzhalter) ----------------
elif page == "Analyse":
    st.title("Analyse")
    st.write("Hier kommt Analyse-Logik hin")

# ---------------- Seite: Negotiation Configuration ----------------
elif page == "Negotiation Configuration":
    st.title("Negotiation Configuration")

    # Initialize attribute weights in session state if they don't exist, making a deep copy
    if 'buyer_attribute_weights' not in st.session_state:
        st.session_state.buyer_attribute_weights = BUYER_CONFIG["ATTRIBUTE_WEIGHTS"].copy()
    if 'seller_attribute_weights' not in st.session_state:
        st.session_state.seller_attribute_weights = SELLER_CONFIG["ATTRIBUTE_WEIGHTS"].copy()

    buyer_club_name_from_config = CLUB_CONFIG.get("BUYER_CLUB_NAME", "Buyer Club (Not Set)")
    seller_club_name_from_config = CLUB_CONFIG.get("SELLER_CLUB_NAME", "Seller Club (Not Set)")

    st.write(f"Configuring weights for negotiations between **{buyer_club_name_from_config}** and **{seller_club_name_from_config}**.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Weights for {buyer_club_name_from_config} (Buyer)")
        for attr, weight in st.session_state.buyer_attribute_weights.items():
            # Ensure unique keys for sliders
            slider_key_buyer = f"buyer_{attr}"
            new_weight_buyer = st.slider(
                f"{attr.replace('_', ' ').title()}",
                min_value=0.0,
                max_value=5.0,
                value=float(st.session_state.buyer_attribute_weights.get(attr, weight)), # Use .get for safety if key might be missing
                step=0.1,
                key=slider_key_buyer
            )
            st.session_state.buyer_attribute_weights[attr] = new_weight_buyer

    with col2:
        st.subheader(f"Weights for {seller_club_name_from_config} (Seller)")
        for attr, weight in st.session_state.seller_attribute_weights.items():
            # Ensure unique keys for sliders
            slider_key_seller = f"seller_{attr}"
            new_weight_seller = st.slider(
                f"{attr.replace('_', ' ').title()}",
                min_value=0.0,
                max_value=5.0,
                value=float(st.session_state.seller_attribute_weights.get(attr, weight)), # Use .get for safety
                step=0.1,
                key=slider_key_seller
            )
            st.session_state.seller_attribute_weights[attr] = new_weight_seller
    
    st.markdown("---")
    st.write("Current Buyer Weights (Session State):")
    st.json(st.session_state.buyer_attribute_weights)
    st.write("Current Seller Weights (Session State):")
    st.json(st.session_state.seller_attribute_weights)

    st.markdown("---")
    st.subheader("Run Negotiation")

    # Negotiation rounds input
    negotiation_rounds = st.number_input(
        "Number of Negotiation Rounds",
        min_value=1,
        max_value=50000, 
        value=NEGOTIATION_CONFIG.get("MAX_ROUNDS", 1000), 
        step=100,
        key="negotiation_rounds_input"
    )

    if st.button("Start Negotiation", key="start_negotiation_button"):
        # Initialize session state for results if not present
        if 'negotiation_results' not in st.session_state:
            st.session_state.negotiation_results = {}

        st.session_state.negotiation_results['status'] = 'running'
        st.session_state.negotiation_results['log'] = ["Starting negotiation process..."]
        
        # Use a placeholder for detailed log to avoid cluttering the main UI for now
        negotiation_log_placeholder = st.empty() 
        progress_bar = st.progress(0)
        status_text = st.empty() # For brief status updates

        try:
            # 1. Load Club Data
            status_text.text("Loading club data...")
            buyer_club_name = CLUB_CONFIG["BUYER_CLUB_NAME"]
            seller_club_name = CLUB_CONFIG["SELLER_CLUB_NAME"]
            
            # Ensure player data loader uses configured club names without fallback to sample for this UI interaction
            # This assumes load_clubs_from_csv will use CLUB_CONFIG by default if names are not passed,
            # or that it correctly uses the passed names.
            # The previous version of PlayerDataLoader had a fallback, ensure it's handled.
            # Forcing no fallback for UI-driven negotiation:
            _original_fallback_setting = CLUB_CONFIG.get("FALLBACK_TO_SAMPLE_DATA", True)
            CLUB_CONFIG["FALLBACK_TO_SAMPLE_DATA"] = False # Temporarily disable fallback

            try:
                actual_buyer_players, actual_seller_players = ClubBasedPlayerDataLoader.load_clubs_from_csv(
                    buyer_club_name=buyer_club_name, 
                    seller_club_name=seller_club_name
                )
            except ValueError as ve: 
                 st.error(f"Error loading club data: {ve}")
                 st.session_state.negotiation_results['status'] = 'error'
                 st.session_state.negotiation_results['log'].append(f"Error: {ve}")
                 st.stop()
            finally:
                 CLUB_CONFIG["FALLBACK_TO_SAMPLE_DATA"] = _original_fallback_setting # Restore setting

            if not actual_buyer_players or not actual_seller_players:
                error_msg = f"Could not load players for one or both clubs: {buyer_club_name}, {seller_club_name}. Ensure they exist in the CSV and have enough players as per MIN_PLAYERS_REQUIRED."
                st.error(error_msg)
                st.session_state.negotiation_results['status'] = 'error'
                st.session_state.negotiation_results['log'].append(error_msg)
                st.stop()

            st.session_state.negotiation_results['log'].append(f"Data loaded for {buyer_club_name} ({len(actual_buyer_players)} players) and {seller_club_name} ({len(actual_seller_players)} players).")
            progress_bar.progress(10)
            status_text.text("Club data loaded. Initializing agents...")

            # 2. Initialize Agents with session state weights
            buyer_agent = BuyerClubAgent(
                club_name=buyer_club_name, 
                attribute_weights_override=st.session_state.buyer_attribute_weights
            )
            buyer_agent.set_players(copy.deepcopy(actual_buyer_players)) # Use deep copies for agents

            seller_agent = SellerClubAgent(
                club_name=seller_club_name, 
                attribute_weights_override=st.session_state.seller_attribute_weights
            )
            seller_agent.set_players(copy.deepcopy(actual_seller_players)) # Use deep copies for agents
            
            st.session_state.negotiation_results['log'].append(f"Agents initialized for {buyer_agent.club_name} and {seller_agent.club_name}.")
            progress_bar.progress(20)
            status_text.text("Agents initialized. Initializing mediator...")

            # 3. Initialize Mediator
            mediator = ClubBasedFootballMediator(
                buyer_agent.players, seller_agent.players # Agents now hold the player pools for negotiation
            )
            st.session_state.negotiation_results['log'].append("Mediator initialized.")
            progress_bar.progress(30)
            status_text.text("Mediator initialized. Starting negotiation rounds...")

            # 4. Run Negotiation Loop (adapted from AgentenSystem/main.py's run_club_negotiation)
            st.session_state.initial_buyer_players = copy.deepcopy(buyer_agent.players)
            st.session_state.initial_seller_players = copy.deepcopy(seller_agent.players)
            initial_buyer_utility = buyer_agent.calculate_utility_for_hypothetical_squad(buyer_agent.players)
            initial_seller_utility = seller_agent.calculate_utility_for_hypothetical_squad(seller_agent.players)

            accepted_inter_club_swaps = 0
            
            # Temporarily suppress extensive console logging from the imported modules for a cleaner Streamlit experience
            original_show_detailed_start_info = DISPLAY_CONFIG.get("SHOW_DETAILED_START_INFO", True)
            DISPLAY_CONFIG["SHOW_DETAILED_START_INFO"] = False # Suppress some logs

            for i in range(negotiation_rounds):
                proposed_buyer_player_to_give, proposed_seller_player_to_give = mediator.propose_inter_club_swap()

                if proposed_buyer_player_to_give is None or proposed_seller_player_to_give is None:
                    msg = f"Round {i+1}: No valid inter-club swap can be proposed (pools too small?). Ending negotiation early."
                    st.session_state.negotiation_results['log'].append(msg)
                    status_text.warning(msg)
                    break

                buyer_accepted = buyer_agent.vote(proposed_buyer_player_to_give, proposed_seller_player_to_give)
                seller_accepted = seller_agent.vote(proposed_seller_player_to_give, proposed_buyer_player_to_give)
                
                trade_executed = False
                if buyer_accepted and seller_accepted:
                    try:
                        buyer_agent.players.remove(proposed_buyer_player_to_give)
                        buyer_agent.players.append(proposed_seller_player_to_give)
                        seller_agent.players.remove(proposed_seller_player_to_give)
                        seller_agent.players.append(proposed_buyer_player_to_give)
                        accepted_inter_club_swaps += 1
                        trade_executed = True
                        st.session_state.negotiation_results['log'].append(
                           f"Round {i+1}: Trade ACCEPTED. {buyer_agent.club_name} gives {proposed_buyer_player_to_give.name} for {proposed_seller_player_to_give.name}.")
                    except ValueError: 
                        st.session_state.negotiation_results['log'].append(f"Round {i+1}: Error executing trade, player not found in list.")
                        trade_executed = False
                else:
                    st.session_state.negotiation_results['log'].append(
                        f"Round {i+1}: Trade REJECTED. Buyer: {'Accepted' if buyer_accepted else 'Rejected'}, Seller: {'Accepted' if seller_accepted else 'Rejected'}")

                mediator.record_trade_decision(
                    proposed_buyer_player_to_give, proposed_seller_player_to_give,
                    buyer_accepted, seller_accepted, trade_executed
                )
                
                progress_bar.progress(30 + int(((i+1) / negotiation_rounds) * 65)) # Update progress bar
                if (i+1) % 50 == 0 or (i+1) == negotiation_rounds: # Update text less frequently
                     status_text.text(f"Negotiation Round {i+1}/{negotiation_rounds}... Accepted Trades: {accepted_inter_club_swaps}")
            
            DISPLAY_CONFIG["SHOW_DETAILED_START_INFO"] = original_show_detailed_start_info # Restore logging setting

            progress_bar.progress(95)
            status_text.text("Negotiation loop completed. Storing results...")

            # 5. Store Results
            st.session_state.final_buyer_players = buyer_agent.players
            st.session_state.final_seller_players = seller_agent.players
            st.session_state.trade_history = mediator.trade_log
            st.session_state.negotiation_summary = {
                "buyer_club": buyer_club_name,
                "seller_club": seller_club_name,
                "rounds_conducted": negotiation_rounds, # This is the requested rounds
                "actual_rounds_completed": i + 1 if proposed_buyer_player_to_give and proposed_seller_player_to_give else i, # Actual rounds before potential early break
                "accepted_swaps": accepted_inter_club_swaps,
                "initial_buyer_utility": initial_buyer_utility,
                "final_buyer_utility": buyer_agent.calculate_utility_for_hypothetical_squad(buyer_agent.players),
                "initial_seller_utility": initial_seller_utility,
                "final_seller_utility": seller_agent.calculate_utility_for_hypothetical_squad(seller_agent.players),
            }
            st.session_state.negotiation_results['status'] = 'completed'
            st.session_state.negotiation_results['log'].append("Negotiation complete!")
            st.session_state.negotiation_results['summary'] = st.session_state.negotiation_summary


            progress_bar.progress(100)
            status_text.success("Negotiation complete! Results are stored. View them on the 'Results Visualization' page (to be implemented).")
            st.balloons()

        except FileNotFoundError as fnf_error:
            st.error(f"Failed to load data: {fnf_error}. Ensure '{fnf_error.filename}' is available.")
            st.session_state.negotiation_results['status'] = 'error'
            st.session_state.negotiation_results['log'].append(f"Failed to load data: {fnf_error}")
        except Exception as e:
            st.error(f"An unexpected error occurred during negotiation: {e}")
            import traceback
            detailed_error = traceback.format_exc()
            st.text_area("Error Details", detailed_error, height=200)
            st.session_state.negotiation_results['status'] = 'error'
            st.session_state.negotiation_results['log'].append(f"Unexpected error: {e}\n{detailed_error}")
            status_text.error("Negotiation failed.")

# ---------------- Seite: Negotiation Results ----------------
elif page == "Negotiation Results":
    st.title("Negotiation Results")

    if 'negotiation_summary' not in st.session_state or \
       'initial_buyer_players' not in st.session_state or \
       'final_buyer_players' not in st.session_state or \
       'initial_seller_players' not in st.session_state or \
       'final_seller_players' not in st.session_state or \
       'trade_history' not in st.session_state:
        st.warning("Please run a negotiation on the 'Negotiation Configuration' page first to see results.")
        st.stop()

    summary = st.session_state.negotiation_summary
    initial_buyer_players = st.session_state.initial_buyer_players
    final_buyer_players = st.session_state.final_buyer_players
    initial_seller_players = st.session_state.initial_seller_players
    final_seller_players = st.session_state.final_seller_players
    trade_history = st.session_state.trade_history

    # 1. Display Negotiation Summary
    st.subheader("Negotiation Summary")
    
    col1_sum, col2_sum = st.columns(2)
    with col1_sum:
        st.metric(label=f"{summary['buyer_club']} Initial Utility", value=f"{summary['initial_buyer_utility']:.2f}")
        st.metric(label=f"{summary['buyer_club']} Final Utility", value=f"{summary['final_buyer_utility']:.2f}", delta=f"{summary['final_buyer_utility'] - summary['initial_buyer_utility']:.2f}")
    with col2_sum:
        st.metric(label=f"{summary['seller_club']} Initial Utility", value=f"{summary['initial_seller_utility']:.2f}")
        st.metric(label=f"{summary['seller_club']} Final Utility", value=f"{summary['final_seller_utility']:.2f}", delta=f"{summary['final_seller_utility'] - summary['initial_seller_utility']:.2f}")

    st.write(f"Total Rounds Conducted: {summary['rounds_conducted']}")
    st.write(f"Actual Rounds Completed (before potential early stop): {summary['actual_rounds_completed']}")
    st.write(f"Total Successful Swaps: {summary['accepted_swaps']}")
    st.markdown("---")

    # 2. Visualize Squads (Before and After)
    st.subheader("Squad Changes")
    col_buyer, col_seller = st.columns(2)

    def get_player_details_df(player_list):
        if not player_list:
            return pd.DataFrame(columns=['Name', 'Age', 'Value ($)', 'Overall (Example)']) # Adjust columns as needed
        
        data = []
        for p in player_list:
            # Assuming 'overall' is a combination of some attributes, or a direct one if available.
            # For now, using a placeholder or simple sum. This should be adapted if Player class changes.
            # Example: (p.finishing + p.dribbling + p.reactions) / 3 
            # For now, just using a placeholder value, as 'overall' is not directly on Player.
            # If PlayerAgent's evaluate_player is accessible and cheap, it could be used.
            # Let's use player value as a proxy or a key attribute like finishing.
            data.append({'Name': p.name, 'Age': p.age, 'Value ($)': p.value, 'Finishing': p.finishing})
        return pd.DataFrame(data)

    with col_buyer:
        st.markdown(f"**{summary['buyer_club']} (Buyer)**")
        with st.expander("Initial Squad", expanded=False):
            st.dataframe(get_player_details_df(initial_buyer_players))
        with st.expander("Final Squad", expanded=True):
            st.dataframe(get_player_details_df(final_buyer_players))
            
    with col_seller:
        st.markdown(f"**{summary['seller_club']} (Seller)**")
        with st.expander("Initial Squad", expanded=False):
            st.dataframe(get_player_details_df(initial_seller_players))
        with st.expander("Final Squad", expanded=True):
            st.dataframe(get_player_details_df(final_seller_players))
    st.markdown("---")

    # 3. Display Trade History Log
    st.subheader("Trade History Log")
    if trade_history:
        trade_df = pd.DataFrame(trade_history)
        # Reorder columns for better readability
        cols_order = ['buyer_player_offered_name', 'seller_player_offered_name', 'buyer_accepted', 'seller_accepted', 'trade_executed']
        # Filter out columns not in the DataFrame to prevent errors if some are missing
        trade_df_display = trade_df[[col for col in cols_order if col in trade_df.columns]]
        st.dataframe(trade_df_display)
    else:
        st.write("No trades were attempted or logged.")
    st.markdown("---")
    
    # 4. Plot Utility Score Comparison (Bar Chart)
    st.subheader("Utility Score Comparison (Initial vs. Final)")
    
    utility_data = {
        'Club': [summary['buyer_club'], summary['buyer_club'], summary['seller_club'], summary['seller_club']],
        'Stage': ['Initial', 'Final', 'Initial', 'Final'],
        'Utility': [
            summary['initial_buyer_utility'], summary['final_buyer_utility'],
            summary['initial_seller_utility'], summary['final_seller_utility']
        ]
    }
    utility_df = pd.DataFrame(utility_data)
    
    fig_utility, ax_utility = plt.subplots()
    # Using seaborn's barplot can make this prettier if seaborn is available, but sticking to matplotlib for now.
    # Create grouped bar chart:
    pivot_df = utility_df.pivot(index='Club', columns='Stage', values='Utility')
    pivot_df.plot(kind='bar', ax=ax_utility, rot=0)
    
    ax_utility.set_ylabel("Utility Score")
    ax_utility.set_title("Club Utility Scores: Initial vs. Final")
    ax_utility.legend(title="Stage")
    st.pyplot(fig_utility)
    
    # Display detailed negotiation log if available
    if 'log' in st.session_state.negotiation_results and st.session_state.negotiation_results['log']:
        with st.expander("Show Detailed Negotiation Log"):
            st.text_area("", "\n".join(st.session_state.negotiation_results['log']), height=300)


    st.markdown("---")
    st.subheader("Run Negotiation")

    # Negotiation rounds input
    negotiation_rounds = st.number_input(
        "Number of Negotiation Rounds",
        min_value=1,
        max_value=50000, # Max rounds from config is 15000, but allow higher for UI testing
        value=NEGOTIATION_CONFIG.get("MAX_ROUNDS", 1000), # Default from config
        step=100,
        key="negotiation_rounds_input"
    )

    if st.button("Start Negotiation", key="start_negotiation_button"):
        st.write("Starting negotiation process...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # 1. Load Club Data
            status_text.text("Loading club data...")
            buyer_club_name = CLUB_CONFIG["BUYER_CLUB_NAME"]
            seller_club_name = CLUB_CONFIG["SELLER_CLUB_NAME"]
            
            # Use ClubBasedPlayerDataLoader
            # Ensure FALLBACK_TO_SAMPLE_DATA is False for this UI-driven negotiation if desired,
            # or handle it appropriately. For now, use default config behavior.
            # We might want to make FALLBACK_TO_SAMPLE_DATA configurable in UI later.
            cfg_copy = copy.deepcopy(CLUB_CONFIG) # Make a deep copy for modification
            cfg_copy['FALLBACK_TO_SAMPLE_DATA'] = False # Ensure it errors if clubs not found
            
            try:
                # Temporarily override CLUB_CONFIG for the loader if necessary, or pass directly
                # For simplicity, assuming load_clubs_from_csv can take names directly or uses CLUB_CONFIG
                # The loader uses CLUB_CONFIG by default if names are not passed.
                # To ensure it uses the *correctly configured* names for this session:
                # We can pass them directly.
                actual_buyer_players, actual_seller_players = ClubBasedPlayerDataLoader.load_clubs_from_csv(
                    buyer_club_name=buyer_club_name, 
                    seller_club_name=seller_club_name
                )
            except ValueError as ve: # Catch specific error if clubs have too few players
                 st.error(f"Error loading club data: {ve}")
                 st.stop() # Stop execution for this button press
            
            if not actual_buyer_players or not actual_seller_players:
                st.error(f"Could not load players for one or both clubs: {buyer_club_name}, {seller_club_name}. Ensure they exist in the CSV and have enough players as per MIN_PLAYERS_REQUIRED.")
                st.stop()

            progress_bar.progress(10)
            status_text.text("Club data loaded. Initializing agents...")

            # 2. Initialize Agents with session state weights
            # The agent __init__ methods were refactored to accept attribute_weights_override
            buyer_agent = BuyerClubAgent(
                club_name=buyer_club_name, 
                attribute_weights_override=st.session_state.buyer_attribute_weights
            )
            buyer_agent.set_players(actual_buyer_players)

            seller_agent = SellerClubAgent(
                club_name=seller_club_name, 
                attribute_weights_override=st.session_state.seller_attribute_weights
            )
            seller_agent.set_players(actual_seller_players)
            
            progress_bar.progress(20)
            status_text.text("Agents initialized. Initializing mediator...")

            # 3. Initialize Mediator
            mediator = ClubBasedFootballMediator(
                buyer_agent.players, seller_agent.players
            )
            progress_bar.progress(30)
            status_text.text("Mediator initialized. Starting negotiation rounds...")

            # 4. Run Negotiation Loop (adapted from AgentenSystem/main.py)
            # Store initial player lists for comparison, using deepcopy for safety if Player objects are mutable in other ways
            st.session_state.initial_buyer_players = [copy.deepcopy(p) for p in buyer_agent.players]
            st.session_state.initial_seller_players = [copy.deepcopy(p) for p in seller_agent.players]

            accepted_inter_club_swaps = 0
            
            # Disable verbose console logging from agents/mediator for Streamlit UI
            # by temporarily overriding relevant LOGGING_CONFIG settings if needed.
            # This part is tricky without direct control over the imported module's config at runtime for prints.
            # For now, we accept console output will happen.
            # A better way would be for those classes to accept a logger object or verbosity level.

            for i in range(negotiation_rounds):
                proposed_buyer_player_to_give, proposed_seller_player_to_give = mediator.propose_inter_club_swap()

                if proposed_buyer_player_to_give is None or proposed_seller_player_to_give is None:
                    status_text.warning(f"Round {i+1}: No valid inter-club swap can be proposed. Ending negotiation early.")
                    break

                buyer_accepted = buyer_agent.vote(proposed_buyer_player_to_give, proposed_seller_player_to_give)
                seller_accepted = seller_agent.vote(proposed_seller_player_to_give, proposed_buyer_player_to_give)
                
                trade_executed = False
                if buyer_accepted and seller_accepted:
                    try:
                        buyer_agent.players.remove(proposed_buyer_player_to_give)
                        buyer_agent.players.append(proposed_seller_player_to_give)
                        seller_agent.players.remove(proposed_seller_player_to_give)
                        seller_agent.players.append(proposed_buyer_player_to_give)
                        accepted_inter_club_swaps += 1
                        trade_executed = True
                    except ValueError: # Player not found, should not happen if logic is correct
                        st.warning(f"Round {i+1}: Error executing trade, player not found in list.")
                        trade_executed = False # Ensure it's false

                mediator.record_trade_decision(
                    proposed_buyer_player_to_give, proposed_seller_player_to_give,
                    buyer_accepted, seller_accepted, trade_executed
                )
                
                progress_bar.progress(30 + int((i / negotiation_rounds) * 60))
                if i % 100 == 0 or i == negotiation_rounds -1 : # Update text less frequently
                     status_text.text(f"Negotiation Round {i+1}/{negotiation_rounds}... Trades: {accepted_inter_club_swaps}")


            progress_bar.progress(95)
            status_text.text("Negotiation loop completed. Storing results...")

            # 5. Store Results
            st.session_state.final_buyer_players = buyer_agent.players
            st.session_state.final_seller_players = seller_agent.players
            st.session_state.trade_history = mediator.trade_log
            st.session_state.negotiation_summary = {
                "buyer_club": buyer_club_name,
                "seller_club": seller_club_name,
                "rounds_conducted": negotiation_rounds,
                "accepted_swaps": accepted_inter_club_swaps,
                "initial_buyer_utility": buyer_agent.calculate_utility_for_hypothetical_squad(st.session_state.initial_buyer_players),
                "final_buyer_utility": buyer_agent.calculate_utility_for_hypothetical_squad(st.session_state.final_buyer_players),
                "initial_seller_utility": seller_agent.calculate_utility_for_hypothetical_squad(st.session_state.initial_seller_players),
                "final_seller_utility": seller_agent.calculate_utility_for_hypothetical_squad(st.session_state.final_seller_players),
            }

            progress_bar.progress(100)
            status_text.success("Negotiation complete! Results are stored. View them on the 'Results Visualization' page.")
            st.balloons()

        except FileNotFoundError as fnf_error:
            st.error(f"Failed to load data: {fnf_error}. Ensure '{fnf_error.filename}' is available.")
        except Exception as e:
            st.error(f"An unexpected error occurred during negotiation: {e}")
            import traceback
            st.text(traceback.format_exc())
            status_text.error("Negotiation failed.")
