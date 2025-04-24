import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')  # hübscher Stils
# Navigation
page = st.selectbox("Seite wählen", ["Start", "Vereinswahl"] )
df = pd.read_csv( "player_stats.csv" , encoding="latin1")
# Seite: Start
if page == "Start":
    st.title("Rohdaten")
    st.dataframe(df)
# Seite: Verein Wählen
elif page == "Vereinswahl":
    st.title("Verein wählen")
    df_club = df[["player", "club"]]

# Einzigartige Clubs extrahieren
    clubs = sorted(df["club"].dropna().unique())
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

    # Plot: korrekt ohne Transpose
    st.subheader("Visualisierung")
    fig, ax = plt.subplots(figsize=(10, 6))
    agg_df[selected_cols].T.plot(kind="bar", ax=ax)
    ax.set_title(f"{aggregation} Vergleich: {club1} vs. {club2}")
    ax.set_xlabel("Attribut")
    ax.set_ylabel("Wert")
    ax.legend(title="Club")
    st.pyplot(fig)

    # Tabelle (optional)
    st.subheader("Tabelle der aggregierten Werte")
    st.dataframe(agg_df[selected_cols].style.format("{:.2f}"))
# Seite: Analyse
elif page == "Analyse":
    st.title("Analyse")
    st.write("Hier kommt Analyse-Logik hin")
