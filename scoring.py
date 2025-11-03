import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

# ------------------- HELPERS -------------------

def position_calcul(pos):
    """Normalize position strings safely."""
    if pd.isna(pos):
        return "MID"  # default if missing

    pos = str(pos).strip()  # ensure it's a string

    if len(pos) > 2:
        final_pos = pos.split(",")[0].strip()
    else:
        final_pos = pos

    if final_pos.endswith("W"):
        return "FWD"
    elif final_pos.endswith("M"):
        return "MID"
    elif final_pos.endswith("B"):
        return "DEF"
    else:
        return "UNK"  # fallback

# ------------------- SCORING FUNCTIONS -------------------

def def_score_calc(df):
    team_conc = df.get("goals_conceded", 0)
    score = (
        1.9 * df.get("Aerial Duels_Won", 0)
        - 1.5 * df.get("Aerial Duels_Lost", 0)
        + 2.7 * df.get("Performance_Tkl", 0)
        - 1.6 * df.get("Challenges_Lost", 0)
        + 2.7 * df.get("Performance_Int", 0)
        + 1.1 * df.get("Unnamed: 20_level_0_Clr", 0)
        + (10 - (5 * team_conc))
        + df.get("Passes_Cmp", 0) / 9
        - ((df.get("Passes_Att", 0) - df.get("Passes_Cmp", 0)) / 4.5)
        + df.get("Unnamed: 23_level_0_KP", 0)
        + df.get("Take-Ons_Succ", 0) * 2.5
        + 1.1 * df.get("Blocks_Sh", 0)
        + df.get("Performance_SoT", 0) * 2.5
        + df.get("Performance_Gls", 0) * 10
        + df.get("Performance_Ast", 0) * 8
        - 5 * df.get("Performance_CrdR", 0)
    )
    return round(score, 0)

def mid_score_calc(df):
    team_conc = df.get("goals_conceded", 0)
    team_score = df.get("goals_scored", 0)
    score = (
        1.7 * df.get("Aerial Duels_Won", 0)
        + 2.6 * df.get("Performance_Tkl", 0)
        + 2.5 * df.get("Performance_Int", 0)
        + (4 - (2 * team_conc) + (2 * team_score))
        + df.get("Passes_Cmp", 0) / 6.6
        - ((df.get("Passes_Att", 0) - df.get("Passes_Cmp", 0)) / 3.2)
        + df.get("Unnamed: 23_level_0_KP", 0)
        + df.get("Take-Ons_Succ", 0) * 2.9
        + 2.2 * df.get("Performance_SoT", 0)
        + df.get("Performance_Gls", 0) * 10
        + df.get("Performance_Ast", 0) * 8
        - 5 * df.get("Performance_CrdR", 0)
    )
    return round(score, 0)

def fwd_score_calc(df):
    team_score = df.get("goals_scored", 0)
    score = (
        1.4 * df.get("Aerial Duels_Won", 0)
        + 2.6 * df.get("Performance_Tkl", 0)
        + 2.7 * df.get("Performance_Int", 0)
        + (3 * team_score)
        + df.get("Passes_Cmp", 0) / 6
        + df.get("Unnamed: 23_level_0_KP", 0)
        + df.get("Take-Ons_Succ", 0) * 3.0
        + df.get("Performance_SoT", 0) * 3.0
        + df.get("Performance_Gls", 0) * 10
        + df.get("Performance_Ast", 0) * 8
        - 5 * df.get("Performance_CrdR", 0)
    )
    return round(score, 0)

# ------------------- TABLE PARSING -------------------

def parse_team_tables_from_html(html_content):
    """Find both home and away player stats tables dynamically."""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")

    team_tables = []
    for table in tables:
        caption = table.find("caption")
        if caption and "Player Stats Table" in caption.text:
            team_tables.append(table)

    if not team_tables:
        raise ValueError("No team player stats tables found in the HTML.")

    dataframes = [pd.read_html(str(t))[0] for t in team_tables]
    if len(dataframes) == 1:
        df_home, df_away = dataframes[0], pd.DataFrame()
    else:
        df_home, df_away = dataframes[0], dataframes[1]

    st.write("✅ Found", len(dataframes), "team tables in HTML.")
    return df_home, df_away


def normalize_columns(df, label=""):
    """Flatten multi-index columns and make them easier to match."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            "_".join([str(x) for x in col if str(x) != "nan"]).strip("_")
            for col in df.columns
        ]
    else:
        df.columns = [str(c) for c in df.columns]

    df.columns = [c.replace("Unnamed: 0_level_0_", "").replace("Unnamed: ", "").strip() for c in df.columns]
    st.write(f"📊 Columns in {label} table after normalization:", df.columns.tolist())
    return df


def calc_all_players_from_html(html_content):
    """Parse HTML and calculate fantasy scores for all players."""
    df_home, df_away = parse_team_tables_from_html(html_content)

    def process_df(df, team_type):
        if df.empty:
            return pd.DataFrame()
        df = normalize_columns(df, team_type)

        # Identify 'Player' column
        player_col = next((c for c in df.columns if "player" in c.lower()), None)
        if not player_col:
            st.error(f"❌ Could not find 'Player' column in {team_type} table. Columns: {df.columns.tolist()}")
            raise ValueError("Could not find 'Player' column after normalization.")

        df = df.rename(columns={player_col: "Player"})

        # Identify 'Pos' column
        if "Pos" not in df.columns:
            pos_col = next((c for c in df.columns if "pos" in c.lower()), None)
            if pos_col:
                df = df.rename(columns={pos_col: "Pos"})
            else:
                st.warning(f"⚠️ No 'Pos' column found in {team_type} table. Defaulting all to MID.")
                df["Pos"] = "MID"

        st.write(f"🧩 Sample data for {team_type} team:")
        st.write(df.head())

        # Apply fantasy scoring
        df["Team"] = team_type
        df["pos"] = df["Pos"].apply(position_calcul)
        df["score"] = df.apply(
            lambda row: (
                fwd_score_calc(row)
                if row["pos"] == "FWD"
                else mid_score_calc(row)
                if row["pos"] == "MID"
                else def_score_calc(row)
            ),
            axis=1,
        )

        return df[["Player", "Team", "pos", "score"]]

    df_home_scored = process_df(df_home, "Home")
    df_away_scored = process_df(df_away, "Away")

    combined = pd.concat([df_home_scored, df_away_scored], ignore_index=True)
    st.write("✅ Combined data preview:")
    st.write(combined.head())
    return combined
