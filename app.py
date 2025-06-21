# app.py - Mit Attribut-Gewichtungs-Slidern
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import sys

# Import UNSERER Module
try:
    from data_class import *
    from PlayerDataLoader import PlayerDataLoader
    from ClubAgent import ClubAgent
    from TransferMarket import TransferMarket
    from FootballMediator import FootballMediator
    from config import *
except ImportError as e:
    st.error(f"Import-Fehler: {e}")
    st.error("Stelle sicher, dass alle Module im gleichen Verzeichnis sind!")
    st.stop()

# Setze Default für ANALYSIS_CONFIG falls nicht definiert
if 'ANALYSIS_CONFIG' not in globals():
    ANALYSIS_CONFIG = {
        "KEY_ATTRIBUTES": ["finishing", "vision", "stamina", "heading", 
                          "ball_control", "short_pass", "slide_tackle", "sprint_speed"]
    }

# Seiten-Konfiguration
st.set_page_config(
    page_title="⚽ Fußball Transfer System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    .transfer-card {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .club-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .strategy-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px;
    }
    .attribute-group {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# Attribut-Kategorien für bessere Organisation
ATTRIBUTE_CATEGORIES = {
    "⚡ Offensive": ["finishing", "shot_power", "att_position", "long_shots", "volleys"],
    "🎯 Technik": ["ball_control", "dribbling", "vision", "composure", "curve"],
    "📬 Pässe": ["short_pass", "long_pass", "crossing", "fk_acc"],
    "🛡️ Defensive": ["slide_tackle", "stand_tackle", "interceptions", "heading"],
    "🏃 Physis": ["acceleration", "sprint_speed", "stamina", "strength", "balance", "agility", "jumping"],
    "🧠 Mental": ["reactions", "aggression", "penalties"]
}

# Alle Attribute für die vollständige Liste
ALL_ATTRIBUTES = [
    "ball_control", "dribbling", "slide_tackle", "stand_tackle",
    "aggression", "reactions", "att_position", "interceptions",
    "vision", "composure", "crossing", "short_pass", "long_pass",
    "acceleration", "stamina", "strength", "balance", "sprint_speed",
    "agility", "jumping", "heading", "shot_power", "finishing", "long_shots"
]


class TransferSystemApp:
    """Hauptklasse für die Streamlit-Anwendung"""
    
    def __init__(self):
        # Session State initialisieren
        if 'players_by_club' not in st.session_state:
            st.session_state.players_by_club = None
        if 'transfer_history' not in st.session_state:
            st.session_state.transfer_history = []
        if 'negotiation_results' not in st.session_state:
            st.session_state.negotiation_results = None
        if 'custom_weights_club1' not in st.session_state:
            st.session_state.custom_weights_club1 = {}
        if 'custom_weights_club2' not in st.session_state:
            st.session_state.custom_weights_club2 = {}
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
            
    def load_data(self):
        """Lädt Spielerdaten aus CSV"""
        try:
            # Session State zurücksetzen für frische Daten
            st.session_state.players_by_club = None
            
            with st.spinner("Lade Spielerdaten..."):
                players_by_club = PlayerDataLoader.load_players_by_club()
                
                # Bereinige Daten
                for club in players_by_club:
                    players_by_club[club] = [p for p in players_by_club[club] 
                                           if p.name != "Unknown" and p.name]
                
                # Filtere Vereine mit zu wenigen Spielern
                valid_clubs = {}
                for club, players in players_by_club.items():
                    if len(players) >= 5:
                        valid_clubs[club] = players
                
                st.session_state.players_by_club = valid_clubs
                st.session_state.data_loaded = True
                return True
        except Exception as e:
            st.error(f"Fehler beim Laden der Daten: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
            
    def show_overview_page(self):
        """Zeigt Übersichtsseite mit Datenstatistiken"""
        st.title("📊 Datenübersicht")
        
        if not st.session_state.players_by_club:
            st.warning("Bitte zuerst Daten laden!")
            if st.button("Jetzt Daten laden", type="primary"):
                self.load_data()
                st.rerun()
            return
            
        # Statistiken berechnen
        total_clubs = len(st.session_state.players_by_club)
        total_players = sum(len(players) for players in st.session_state.players_by_club.values())
        
        # Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Vereine", total_clubs)
        with col2:
            st.metric("Spieler", total_players)
        with col3:
            avg_players = total_players / total_clubs if total_clubs > 0 else 0
            st.metric("Ø Spieler/Verein", f"{avg_players:.1f}")
        with col4:
            eligible_clubs = len([c for c, p in st.session_state.players_by_club.items() 
                                if len(p) >= SYSTEM_CONFIG["MIN_PLAYERS_PER_CLUB"]])
            st.metric("Verhandlungsfähige Vereine", eligible_clubs)
            
        # Top Vereine
        st.subheader("🏆 Top 10 Vereine nach Kadergröße")
        club_sizes = [(club, len(players)) for club, players in st.session_state.players_by_club.items()]
        club_sizes.sort(key=lambda x: x[1], reverse=True)
        
        fig = px.bar(
            x=[c[0] for c in club_sizes[:10]],
            y=[c[1] for c in club_sizes[:10]],
            labels={'x': 'Verein', 'y': 'Anzahl Spieler'},
            title="Größte Vereine nach Spieleranzahl"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
    def show_club_analysis_page(self):
        """Zeigt detaillierte Vereinsanalyse"""
        st.title("🏟️ Vereinsanalyse")
        
        if not st.session_state.players_by_club:
            st.warning("Bitte zuerst Daten laden!")
            return
            
        # Verein auswählen
        eligible_clubs = [c for c, p in st.session_state.players_by_club.items() 
                         if len(p) >= 5]
        
        selected_club = st.selectbox(
            "Verein auswählen",
            eligible_clubs,
            format_func=lambda x: f"{x} ({len(st.session_state.players_by_club[x])} Spieler)"
        )
        
        if selected_club:
            players = st.session_state.players_by_club[selected_club]
            
            # Club Info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Kadergröße", len(players))
            with col2:
                ages = [getattr(p, 'age', 0) for p in players]
                valid_ages = [a for a in ages if a > 0]
                avg_age = sum(valid_ages) / len(valid_ages) if valid_ages else 0
                st.metric("Ø Alter", f"{avg_age:.1f}")
            with col3:
                values = [getattr(p, 'value', 0) for p in players]
                total_value = sum(values)
                st.metric("Gesamtwert", f"${total_value/1000000:.1f}M")
            with col4:
                avg_value = total_value / len(players) if players else 0
                st.metric("Ø Wert", f"${avg_value/1000000:.2f}M")
                
            # Top Spieler
            st.subheader("⭐ Top 5 wertvollste Spieler")
            top_players = sorted(players, key=lambda p: getattr(p, 'value', 0), reverse=True)[:5]
            
            for i, player in enumerate(top_players, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{i}. **{getattr(player, 'name', 'Unknown')}**")
                with col2:
                    age = getattr(player, 'age', 0)
                    st.write(f"Alter: {age}")
                with col3:
                    value = getattr(player, 'value', 0)
                    st.write(f"${value/1000000:.1f}M")
                    
            # Attribut-Radar
            st.subheader("📊 Team-Attribut-Profil")
            
            key_attributes = ANALYSIS_CONFIG["KEY_ATTRIBUTES"]
            avg_attributes = {}
            for attr in key_attributes:
                values = []
                for p in players:
                    if hasattr(p, attr):
                        val = getattr(p, attr, 0)
                        values.append(val)
                if values:
                    avg_attributes[attr] = sum(values) / len(values)
                    
            if avg_attributes:
                fig = go.Figure(data=go.Scatterpolar(
                    r=list(avg_attributes.values()),
                    theta=list(avg_attributes.keys()),
                    fill='toself',
                    name=selected_club
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Team-Attribut-Profil"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
    def show_transfer_negotiation_page(self):
        """Zeigt Transfer-Verhandlungsseite mit Attribut-Gewichtungen"""
        st.title("🤝 Transfer-Verhandlungen")
        
        if not st.session_state.players_by_club:
            st.warning("Bitte zuerst Daten laden!")
            return
            
        # Vereine auswählen
        st.subheader("Vereine für Verhandlung auswählen")
        
        eligible_clubs = PlayerDataLoader.get_clubs_with_min_players(
            st.session_state.players_by_club,
            SYSTEM_CONFIG["MIN_PLAYERS_PER_CLUB"]
        )
        
        if len(eligible_clubs) < 2:
            st.error(f"Nicht genug Vereine mit mindestens {SYSTEM_CONFIG['MIN_PLAYERS_PER_CLUB']} Spielern!")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            club1 = st.selectbox(
                "Verein 1",
                eligible_clubs,
                key="club1",
                format_func=lambda x: f"{x} ({len(st.session_state.players_by_club[x])} Spieler)"
            )
            strategy1 = st.selectbox(
                "Strategie Verein 1",
                ["balanced", "offensive", "defensive", "technical", "custom"],
                key="strategy1",
                help="'custom' erlaubt eigene Attribut-Gewichtungen"
            )
            
        with col2:
            remaining_clubs = [c for c in eligible_clubs if c != club1]
            club2 = st.selectbox(
                "Verein 2",
                remaining_clubs,
                key="club2",
                format_func=lambda x: f"{x} ({len(st.session_state.players_by_club[x])} Spieler)"
            )
            strategy2 = st.selectbox(
                "Strategie Verein 2",
                ["balanced", "offensive", "defensive", "technical", "custom"],
                key="strategy2",
                help="'custom' erlaubt eigene Attribut-Gewichtungen"
            )
            
        # Attribut-Gewichtungen für Verein 1
        if strategy1 == "custom":
            with st.expander(f"⚙️ Attribut-Gewichtungen für {club1}", expanded=True):
                st.info("Stelle die Wichtigkeit jedes Attributs ein (0 = unwichtig, 10 = sehr wichtig)")
                
                custom_weights1 = {}
                
                # Zeige Slider nach Kategorien
                for category, attributes in ATTRIBUTE_CATEGORIES.items():
                    st.markdown(f"**{category}**")
                    cols = st.columns(3)
                    
                    for i, attr in enumerate(attributes):
                        if attr in ALL_ATTRIBUTES:  # Nur Attribute die wir verwenden
                            with cols[i % 3]:
                                # Hole vorherigen Wert oder Standard
                                default_val = st.session_state.custom_weights_club1.get(attr, 5.0)
                                weight = st.slider(
                                    attr.replace("_", " ").title(),
                                    0.0, 10.0, default_val, 0.5,
                                    key=f"w1_{attr}"
                                )
                                custom_weights1[attr] = weight
                
                st.session_state.custom_weights_club1 = custom_weights1
                
                # Vorschau der Top-Attribute
                if custom_weights1:
                    st.markdown("**Top 5 wichtigste Attribute:**")
                    sorted_attrs = sorted(custom_weights1.items(), key=lambda x: x[1], reverse=True)[:5]
                    for attr, weight in sorted_attrs:
                        st.write(f"- {attr.replace('_', ' ').title()}: {weight:.1f}")
                        
        # Attribut-Gewichtungen für Verein 2
        if strategy2 == "custom":
            with st.expander(f"⚙️ Attribut-Gewichtungen für {club2}", expanded=True):
                st.info("Stelle die Wichtigkeit jedes Attributs ein (0 = unwichtig, 10 = sehr wichtig)")
                
                custom_weights2 = {}
                
                # Zeige Slider nach Kategorien
                for category, attributes in ATTRIBUTE_CATEGORIES.items():
                    st.markdown(f"**{category}**")
                    cols = st.columns(3)
                    
                    for i, attr in enumerate(attributes):
                        if attr in ALL_ATTRIBUTES:  # Nur Attribute die wir verwenden
                            with cols[i % 3]:
                                # Hole vorherigen Wert oder Standard
                                default_val = st.session_state.custom_weights_club2.get(attr, 5.0)
                                weight = st.slider(
                                    attr.replace("_", " ").title(),
                                    0.0, 10.0, default_val, 0.5,
                                    key=f"w2_{attr}"
                                )
                                custom_weights2[attr] = weight
                
                st.session_state.custom_weights_club2 = custom_weights2
                
                # Vorschau der Top-Attribute
                if custom_weights2:
                    st.markdown("**Top 5 wichtigste Attribute:**")
                    sorted_attrs = sorted(custom_weights2.items(), key=lambda x: x[1], reverse=True)[:5]
                    for attr, weight in sorted_attrs:
                        st.write(f"- {attr.replace('_', ' ').title()}: {weight:.1f}")
            
        # Verhandlungsparameter
        st.subheader("⚙️ Verhandlungsparameter")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            max_rounds = st.number_input(
                "Maximale Runden",
                min_value=100,
                max_value=10000,
                value=2000,
                step=100
            )
        with col2:
            temperature = st.slider(
                "Start-Temperatur",
                min_value=10.0,
                max_value=200.0,
                value=SA_CONFIG["INITIAL_TEMPERATURE"],
                step=10.0,
                help="Höhere Temperatur = mehr Exploration"
            )
        with col3:
            show_live = st.checkbox("Live-Updates", value=True)
            show_details = st.checkbox("Details anzeigen", value=False)
            
        # Gewichtungs-Vergleich anzeigen
        if strategy1 == "custom" or strategy2 == "custom":
            with st.expander("📊 Strategie-Vergleich", expanded=False):
                self.show_strategy_comparison(
                    club1, strategy1, st.session_state.custom_weights_club1,
                    club2, strategy2, st.session_state.custom_weights_club2
                )
            
        # Verhandlung starten
        if st.button("🚀 Verhandlung starten", type="primary", use_container_width=True):
            # Bereite custom weights vor
            weights1 = st.session_state.custom_weights_club1 if strategy1 == "custom" else None
            weights2 = st.session_state.custom_weights_club2 if strategy2 == "custom" else None
            
            self.run_negotiation(
                club1, club2, strategy1, strategy2,
                max_rounds, temperature, show_live, show_details,
                weights1, weights2
            )
            
    def show_strategy_comparison(self, club1, strategy1, weights1, club2, strategy2, weights2):
        """Zeigt Vergleich der Strategien"""
        # Hole Standard-Gewichtungen für nicht-custom Strategien
        if strategy1 != "custom":
            base_weights = {attr: 1.5 for attr in ALL_ATTRIBUTES}
            if strategy1 in STRATEGY_CONFIG:
                multipliers = STRATEGY_CONFIG[strategy1].get("ATTRIBUTE_MULTIPLIERS", {})
                for attr, mult in multipliers.items():
                    if attr in base_weights:
                        base_weights[attr] *= mult
            weights1 = base_weights
            
        if strategy2 != "custom":
            base_weights = {attr: 1.5 for attr in ALL_ATTRIBUTES}
            if strategy2 in STRATEGY_CONFIG:
                multipliers = STRATEGY_CONFIG[strategy2].get("ATTRIBUTE_MULTIPLIERS", {})
                for attr, mult in multipliers.items():
                    if attr in base_weights:
                        base_weights[attr] *= mult
            weights2 = base_weights
            
        # Erstelle Vergleichs-Radar
        common_attrs = list(set(weights1.keys()) & set(weights2.keys()) & set(ALL_ATTRIBUTES))[:12]
        
        if common_attrs:
            fig = go.Figure()
            
            # Normalisiere Werte
            max_w1 = max(weights1.values()) if weights1 else 1
            max_w2 = max(weights2.values()) if weights2 else 1
            
            values1 = [weights1.get(attr, 0) / max_w1 * 10 for attr in common_attrs]
            values2 = [weights2.get(attr, 0) / max_w2 * 10 for attr in common_attrs]
            
            fig.add_trace(go.Scatterpolar(
                r=values1,
                theta=[attr.replace("_", " ").title() for attr in common_attrs],
                fill='toself',
                name=f"{club1} ({strategy1})",
                line_color='#1f77b4'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=values2,
                theta=[attr.replace("_", " ").title() for attr in common_attrs],
                fill='toself',
                name=f"{club2} ({strategy2})",
                line_color='#ff7f0e'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Strategie-Vergleich: Attribut-Gewichtungen"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    def run_negotiation(self, club1_name, club2_name, strategy1, strategy2, 
                       max_rounds, temperature, show_live, show_details,
                       custom_weights1=None, custom_weights2=None):
        """Führt die Verhandlung durch mit optionalen custom weights und Transfer-Tracking"""
        
        # Import TransferTracker falls vorhanden
        try:
            from TransferTracker import TransferTracker
            use_tracker = True
        except ImportError:
            st.warning("TransferTracker nicht gefunden - verwende einfaches Tracking")
            use_tracker = False
        
        # Container für Updates
        progress_container = st.container()
        metrics_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
        with metrics_container:
            col1, col2, col3, col4 = st.columns(4)
            rounds_metric = col1.empty()
            transfers_metric = col2.empty()
            rate_metric = col3.empty()
            time_metric = col4.empty()
            
        # Live Updates Container
        if show_live:
            live_container = st.expander("🔄 Live Transfer-Updates", expanded=True)
        
        # Erstelle Agenten mit custom weights
        club1_agent = ClubAgent(club1_name, strategy1, custom_weights1)
        club2_agent = ClubAgent(club2_name, strategy2, custom_weights2)
        
        # Setze Temperatur
        club1_agent.t = temperature
        club2_agent.t = temperature
        
        # Setze Spieler
        club1_agent.set_original_players(st.session_state.players_by_club[club1_name])
        club2_agent.set_original_players(st.session_state.players_by_club[club2_name])
        
        # Erstelle gemeinsamen Pool
        all_players = (st.session_state.players_by_club[club1_name] + 
                      st.session_state.players_by_club[club2_name])
        club1_agent.set_players(all_players)
        club2_agent.set_players(all_players)
        
        # Initialisiere Transfer-Tracker wenn verfügbar
        if use_tracker:
            tracker = TransferTracker(club1_name, club2_name, all_players)
        
        # Zeige Top-Spieler nach Bewertung
        if show_details:
            with st.expander("🌟 Top-Spieler nach Vereinsbewertung", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{club1_name} Top 5:**")
                    ratings1 = [(p, club1_agent.evaluate_player(p)) for p in all_players]
                    ratings1.sort(key=lambda x: x[1], reverse=True)
                    for i, (player, rating) in enumerate(ratings1[:5], 1):
                        st.write(f"{i}. {getattr(player, 'name', 'Unknown')} - Score: {rating:.0f}")
                        
                with col2:
                    st.write(f"**{club2_name} Top 5:**")
                    ratings2 = [(p, club2_agent.evaluate_player(p)) for p in all_players]
                    ratings2.sort(key=lambda x: x[1], reverse=True)
                    for i, (player, rating) in enumerate(ratings2[:5], 1):
                        st.write(f"{i}. {getattr(player, 'name', 'Unknown')} - Score: {rating:.0f}")
        
        # Mediator
        mediator = FootballMediator(len(all_players), len(all_players))
        
        # Initial Squad
        squad_size = len(st.session_state.players_by_club[club1_name])
        current_squad = mediator.init_squads()
        
        # Initialisiere Tracker wenn verfügbar
        if use_tracker:
            tracker.initialize_squads(current_squad, squad_size)
        
        # Start-Utilities
        initial_utility1 = club1_agent.evaluate_squad(current_squad[:squad_size])
        initial_utility2 = club2_agent.evaluate_squad(current_squad[squad_size:])
        
        # Starte Verhandlung
        start_time = time.time()
        successful_transfers = 0
        transfer_history = []
        
        # Verhandlungsschleife
        for round_num in range(max_rounds):
            # Update Progress
            progress = (round_num + 1) / max_rounds
            progress_bar.progress(progress)
            status_text.text(f"Runde {round_num + 1} von {max_rounds}")
            
            # Generiere Vorschlag
            if round_num % 50 == 0 and round_num > 0:
                proposal = mediator.propose_team_shuffle(
                    current_squad,
                    NEGOTIATION_CONFIG["SHUFFLE_PERCENTAGE"]
                )
            else:
                proposal = mediator.propose_player_swap(current_squad)
                
            # Bewertung
            club1_vote = club1_agent.vote(current_squad[:squad_size], 
                                        proposal[:squad_size])
            club2_vote = club2_agent.vote(current_squad[squad_size:], 
                                        proposal[squad_size:])
            
            if club1_vote and club2_vote:
                successful_transfers += 1
                
                # Transfer tracking
                if use_tracker:
                    transfer_info = tracker.track_transfer(current_squad, proposal, squad_size, round_num)
                    
                    if transfer_info and show_live and successful_transfers <= 20:
                        with live_container:
                            st.markdown(f"""
                            **Transfer #{transfer_info['transfer_num']}** (Runde {transfer_info['round']})
                            - 🔴 {transfer_info['from_club']} gibt ab: **{transfer_info['player_out']['name']}** 
                              (Alter: {transfer_info['player_out']['age']}, Wert: ${transfer_info['player_out']['value']/1e6:.1f}M)
                            - 🟢 {transfer_info['from_club']} erhält: **{transfer_info['player_in']['name']}** 
                              (Alter: {transfer_info['player_in']['age']}, Wert: ${transfer_info['player_in']['value']/1e6:.1f}M)
                            """)
                else:
                    # Einfaches Tracking ohne TransferTracker
                    for i in range(len(current_squad)):
                        if current_squad[i] != proposal[i]:
                            player_idx = current_squad[i]
                            player = all_players[player_idx]
                            
                            transfer_history.append({
                                "round": round_num,
                                "player": getattr(player, 'name', 'Unknown'),
                                "from_position": i,
                                "to_position": proposal.index(player_idx)
                            })
                            
                            if show_live and len(transfer_history) <= 20:
                                with live_container:
                                    if i < squad_size:
                                        st.write(f"**Transfer {successful_transfers}**: "
                                               f"{getattr(player, 'name', 'Unknown')} wechselt Position")
                            break
                        
                current_squad = proposal
                
            # Update Metriken
            if round_num % 100 == 0 or round_num == max_rounds - 1:
                elapsed_time = time.time() - start_time
                rounds_metric.metric("Runden", round_num + 1)
                transfers_metric.metric("Transfers", successful_transfers)
                rate = (successful_transfers / (round_num + 1)) * 100
                rate_metric.metric("Erfolgsrate", f"{rate:.1f}%")
                time_metric.metric("Zeit", f"{elapsed_time:.1f}s")
                
        # Endergebnis
        end_time = time.time()
        duration = end_time - start_time
        
        # Finale Utilities
        final_utility1 = club1_agent.evaluate_squad(current_squad[:squad_size])
        final_utility2 = club2_agent.evaluate_squad(current_squad[squad_size:])
        
        progress_bar.progress(1.0)
        status_text.text("✅ Verhandlung abgeschlossen!")
        
        # Erfolgsmeldung
        st.success(f"Verhandlung abgeschlossen! {successful_transfers} Transfers in {duration:.1f} Sekunden")
        
        # Ergebnis-Zusammenfassung
        st.subheader("📊 Verhandlungsergebnis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {club1_name}")
            st.write(f"Strategie: {strategy1}")
            
            delta1 = final_utility1 - initial_utility1
            st.metric(
                "Utility",
                f"{final_utility1:.0f}",
                f"{delta1:+.0f}",
                delta_color="normal"
            )
            
        with col2:
            st.markdown(f"### {club2_name}")
            st.write(f"Strategie: {strategy2}")
            
            delta2 = final_utility2 - initial_utility2
            st.metric(
                "Utility",
                f"{final_utility2:.0f}",
                f"{delta2:+.0f}",
                delta_color="normal"
            )
        
        # Erweiterte Anzeige wenn TransferTracker verfügbar
        if use_tracker:
            # Hole Transfer-Zusammenfassung
            transfer_summary = tracker.get_transfer_summary()
            club1_final, club2_final = tracker.get_final_squads(current_squad, squad_size)
            
            # Transfer-Bilanz
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Transfer-Bilanz {club1_name}:**")
                st.write(f"- Behaltene Original-Spieler: {transfer_summary['club1']['kept_original']}")
                st.write(f"- Neue Spieler von {club2_name}: {transfer_summary['club1']['received_players']}")
                
            with col2:
                st.write(f"**Transfer-Bilanz {club2_name}:**")
                st.write(f"- Behaltene Original-Spieler: {transfer_summary['club2']['kept_original']}")
                st.write(f"- Neue Spieler von {club1_name}: {transfer_summary['club2']['received_players']}")
            
            # Detaillierte Transfer-Historie
            st.subheader("🔄 Transfer-Historie")
            
            if transfer_summary['transfer_history']:
                # Zeige die letzten 10 Transfers
                recent_transfers = transfer_summary['transfer_history'][-10:]
                
                for transfer in recent_transfers:
                    col1, col2, col3 = st.columns([1, 2, 2])
                    
                    with col1:
                        st.write(f"**Transfer #{transfer['transfer_num']}**")
                        st.caption(f"Runde {transfer['round']}")
                        
                    with col2:
                        st.markdown(f"**{transfer['from_club']}** gibt ab:")
                        player_out = transfer['player_out']
                        st.write(f"🔴 {player_out['name']}")
                        st.caption(f"Alter: {player_out['age']}, Wert: ${player_out['value']/1e6:.1f}M")
                        
                    with col3:
                        st.markdown(f"**{transfer['from_club']}** erhält:")
                        player_in = transfer['player_in']
                        st.write(f"🟢 {player_in['name']}")
                        st.caption(f"Alter: {player_in['age']}, Wert: ${player_in['value']/1e6:.1f}M")
                        
                    st.divider()
            else:
                st.info("Keine Transfers durchgeführt.")
            
            # Finale Kader
            st.subheader("👥 Finale Kader")
            
            tab1, tab2 = st.tabs([f"{club1_name}", f"{club2_name}"])
            
            with tab1:
                st.markdown(f"### Finaler Kader {club1_name}")
                
                # Sortiere nach Original/Neu
                original_players_c1 = [p for p in club1_final if p.club == club1_name]
                new_players_c1 = [p for p in club1_final if p.club != club1_name]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏠 Original-Spieler:**")
                    for player in sorted(original_players_c1, key=lambda p: club1_agent.evaluate_player(p), reverse=True):
                        rating = club1_agent.evaluate_player(player)
                        st.write(f"- {player.name} (Rating: {rating:.0f})")
                        
                with col2:
                    st.markdown(f"**🆕 Neue Spieler von {club2_name}:**")
                    for player in sorted(new_players_c1, key=lambda p: club1_agent.evaluate_player(p), reverse=True):
                        rating = club1_agent.evaluate_player(player)
                        st.write(f"- {player.name} (Rating: {rating:.0f})")
                        
            with tab2:
                st.markdown(f"### Finaler Kader {club2_name}")
                
                # Sortiere nach Original/Neu
                original_players_c2 = [p for p in club2_final if p.club == club2_name]
                new_players_c2 = [p for p in club2_final if p.club != club2_name]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏠 Original-Spieler:**")
                    for player in sorted(original_players_c2, key=lambda p: club2_agent.evaluate_player(p), reverse=True):
                        rating = club2_agent.evaluate_player(player)
                        st.write(f"- {player.name} (Rating: {rating:.0f})")
                        
                with col2:
                    st.markdown(f"**🆕 Neue Spieler von {club1_name}:**")
                    for player in sorted(new_players_c2, key=lambda p: club2_agent.evaluate_player(p), reverse=True):
                        rating = club2_agent.evaluate_player(player)
                        st.write(f"- {player.name} (Rating: {rating:.0f})")
        else:
            # Einfache Anzeige ohne TransferTracker
            # Spielerverteilung
            final_players1 = [all_players[i] for i in current_squad[:squad_size]]
            original_count1 = sum(1 for p in final_players1 if getattr(p, 'club', '') == club1_name)
            
            final_players2 = [all_players[i] for i in current_squad[squad_size:]]
            original_count2 = sum(1 for p in final_players2 if getattr(p, 'club', '') == club2_name)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Originale Spieler: {original_count1}/{squad_size}")
            with col2:
                st.write(f"Originale Spieler: {original_count2}/{len(final_players2)}")
        
        # Statistiken
        st.subheader("📈 Verhandlungsstatistiken")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Gesamtrunden", f"{max_rounds:,}")
        with col2:
            st.metric("Erfolgreiche Transfers", successful_transfers)
        with col3:
            st.metric("Erfolgsrate", f"{(successful_transfers/max_rounds)*100:.1f}%")
        with col4:
            st.metric("Transfers/Sekunde", f"{successful_transfers/duration:.2f}")
            
    def run(self):
        """Haupt-Ausführungsmethode der Streamlit App."""
        
        # Load data on first run or if explicitly requested via a button
        if not st.session_state.get('data_loaded', False):
            if self.load_data():
                st.sidebar.success("Daten erfolgreich geladen!")
            else:
                st.sidebar.error("Daten konnten nicht geladen werden. Bitte überprüfen Sie die Datenquelle und Konfiguration.")
                # Optionally, prevent further execution if data is critical:
                # st.stop() 

        st.sidebar.title("⚽ Navigation")
        
        # Option to reload data from sidebar
        if st.sidebar.button("Daten neu laden", key="sidebar_reload_data"):
            if self.load_data():
                st.sidebar.success("Daten erfolgreich neu geladen!")
                st.rerun() # Rerun to reflect changes immediately
            else:
                st.sidebar.error("Erneutes Laden der Daten fehlgeschlagen.")


        page_options = {
            "Datenübersicht": self.show_overview_page,
            "Vereinsanalyse": self.show_club_analysis_page,
            "Transfer-Verhandlungen": self.show_transfer_negotiation_page
        }
        
        selected_page_key = st.sidebar.radio(
            "Wähle eine Seite:",
            list(page_options.keys())
        )
        
        # Call the function for the selected page
        page_function_to_call = page_options[selected_page_key]
        page_function_to_call()

# App starten
if __name__ == "__main__":
    app = TransferSystemApp()
    app.run()