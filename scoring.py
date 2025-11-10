import pandas as pd
from bs4 import BeautifulSoup
import io
import sys

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


def normalize_columns(df, label=""):
    """
    Flatten multi-index columns and clean up names so they match your
    scoring keys like 'Performance_Gls', 'Aerial Duels_Won', etc.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            "_".join([str(x) for x in col if str(x) != "nan"]).strip("_")
            for col in df.columns
        ]
    else:
        df.columns = [str(c) for c in df.columns]

    return df


def find_player_tables(html_content):
    """
    Use pandas to read all tables, then keep only those that have a 'Player'
    column and at least a few rows (to avoid tiny goalkeeper tables, etc.).
    """
    all_tables = pd.read_html(io.StringIO(html_content))
    player_tables = []

    for df in all_tables:
        df = normalize_columns(df)
        # Find a column that looks like 'Player'
        player_col = next(
            (c for c in df.columns if "player" in c.lower()),
            None,
        )
        if player_col is None:
            continue

        # Require a reasonable number of rows to avoid tiny tables
        if df.shape[0] < 5:
            continue

        # Rename the player column to a consistent name
        df = df.rename(columns={player_col: "Player"})
        player_tables.append(df)

    return player_tables


def merge_team_tables(tables):
    """
    Given a list of DataFrames for one team (summary, passing, defensive,
    possession, misc, etc.), merge them horizontally on 'Player'.
    """
    merged = None
    for df in tables:
        df = normalize_columns(df)
        # 'Player' column should already be named "Player"
        if merged is None:
            merged = df
        else:
            merged = merged.merge(df, on="Player", how="left")

    return merged


# ------------------- SCORING FUNCTIONS -------------------

def def_score_calc(row):
    team_conc = row.get("goals_conceded", 0)
    score = (
        1.9 * row.get("Aerial Duels_Won", 0)
        - 1.5 * row.get("Aerial Duels_Lost", 0)
        + 2.7 * row.get("Performance_Tkl", 0)
        - 1.6 * row.get("Challenges_Lost", 0)
        + 2.7 * row.get("Performance_Int", 0)
        + 1.1 * row.get("Unnamed: 20_level_0_Clr", 0)
        + (10 - (5 * team_conc))
        + row.get("Passes_Cmp", 0) / 9
        - ((row.get("Passes_Att", 0) - row.get("Passes_Cmp", 0)) / 4.5)
        + row.get("Unnamed: 23_level_0_KP", 0)
        + row.get("Take-Ons_Succ", 0) * 2.5
        + 1.1 * row.get("Blocks_Sh", 0)
        + row.get("Performance_SoT", 0) * 2.5
        + row.get("Performance_Gls", 0) * 10
        + row.get("Performance_Ast", 0) * 8
        - 5 * row.get("Performance_CrdR", 0)
    )
    return round(score, 0)


def mid_score_calc(row):
    team_conc = row.get("goals_conceded", 0)
    team_score = row.get("goals_scored", 0)
    score = (
        1.7 * row.get("Aerial Duels_Won", 0)
        + 2.6 * row.get("Performance_Tkl", 0)
        + 2.5 * row.get("Performance_Int", 0)
        + (4 - (2 * team_conc) + (2 * team_score))
        + row.get("Passes_Cmp", 0) / 6.6
        - ((row.get("Passes_Att", 0) - row.get("Passes_Cmp", 0)) / 3.2)
        + row.get("Unnamed: 23_level_0_KP", 0)
        + row.get("Take-Ons_Succ", 0) * 2.9
        + 2.2 * row.get("Performance_SoT", 0)
        + row.get("Performance_Gls", 0) * 10
        + row.get("Performance_Ast", 0) * 8
        - 5 * row.get("Performance_CrdR", 0)
    )
    return round(score, 0)


def fwd_score_calc(row):
    team_score = row.get("goals_scored", 0)
    score = (
        1.4 * row.get("Aerial Duels_Won", 0)
        + 2.6 * row.get("Performance_Tkl", 0)
        + 2.7 * row.get("Performance_Int", 0)
        + (3 * team_score)
        + row.get("Passes_Cmp", 0) / 6
        + row.get("Unnamed: 23_level_0_KP", 0)
        + row.get("Take-Ons_Succ", 0) * 3.0
        + row.get("Performance_SoT", 0) * 3.0
        + row.get("Performance_Gls", 0) * 10
        + row.get("Performance_Ast", 0) * 8
        - 5 * row.get("Performance_CrdR", 0)
    )
    return round(score, 0)


# ------------------- MAIN: FROM HTML -------------------

def calc_all_players_from_html(html_content):
    """
    Main entry for Streamlit.
    - reads ALL tables from the FBref HTML
    - keeps only player tables (with 'Player' column)
    - splits them into Home vs Away (first half / second half)
    - merges each team's 6 tables horizontally
    - applies your scoring formulas
    """

    # 1. Find all player tables (summary, passing, def, poss, misc, etc.)
    player_tables = find_player_tables(html_content)

    if len(player_tables) < 2:
        raise ValueError(
            f"Could not find enough player tables in HTML. Found {len(player_tables)}."
        )

    # Assume first half are home, second half are away
    half = len(player_tables) // 2
    home_tables = player_tables[:half]
    away_tables = player_tables[half:]

    # 2. Merge all tables per team
    df_home = merge_team_tables(home_tables)
    df_away = merge_team_tables(away_tables)

    # For now we don't reconstruct goals_scored / goals_conceded from events,
    # so just set them to 0 — this matches the behaviour of your working code.
    df_home["goals_scored"] = 0
    df_home["goals_conceded"] = 0
    df_away["goals_scored"] = 0
    df_away["goals_conceded"] = 0

    # 3. Determine positions and scores

    def process_team(df, team_label):
        # Identify position column
        pos_col = next((c for c in df.columns if c.lower().startswith("pos")), None)
        if pos_col is None:
            df["Pos"] = "MID"
        else:
            df = df.rename(columns={pos_col: "Pos"})

        df["pos"] = df["Pos"].apply(position_calcul)
        df["Team"] = team_label

        def compute_score(row):
            if row["pos"] == "FWD":
                return fwd_score_calc(row)
            elif row["pos"] == "MID":
                return mid_score_calc(row)
            elif row["pos"] == "DEF":
                return def_score_calc(row)
            else:
                return mid_score_calc(row)

        df["score"] = df.apply(compute_score, axis=1)

        return df[["Player", "Team", "pos", "score"]]

    home_scores = process_team(df_home, "Home")
    away_scores = process_team(df_away, "Away")

    combined = pd.concat([home_scores, away_scores], ignore_index=True)
    return combined


# Optional CLI usage (if you want to run locally on an HTML file)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
        with open(html_path, "r", encoding="utf-8") as f:
            html_text = f.read()
        output = "match_output.csv" if len(sys.argv) < 3 else sys.argv[2]
        df = calc_all_players_from_html(html_text)
        df.to_csv(output, index=False)
        print(f"✅ Saved results for {html_path} → {output}")
