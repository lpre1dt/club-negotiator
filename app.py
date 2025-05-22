import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_class import fix_mojibake


# Stil für Matplotlib
plt.style.use('ggplot')

# Seite wählen
page = st.selectbox("Seite wählen", ["Start", "Vereinswahl", "Analyse"])

# Daten einlesen & bereinigen
try:
    df = pd.read_csv("player_stats.csv", encoding="latin1")
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].apply(fix_mojibake)
except Exception as e:
    st.error(f"Fehler beim Laden der Datei: {e}")
    st.stop()
# ---------------- Seite: Rohdaten ----------------
if page == "Start":
    st.title("Rohdaten")
    st.dataframe(df)

# ---------------- Seite: Vereinswahl ----------------
elif page == "Vereinswahl":
    st.title("Verein wählen")
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
