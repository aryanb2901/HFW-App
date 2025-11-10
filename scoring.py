import pandas as pd
from bs4 import BeautifulSoup

# =========================
#  POSITION & SCORING
# =========================

def position_calcul(pos):
    """Normalize position strings safely to FWD / MID / DEF."""
    if pd.isna(pos):
        return "MID"

    pos = str(pos).strip()

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
        return "MID"


def def_score_calc(row):
    team_conc = row.get("goals_conceded", 0) or 0

    score = (
        1.9 * (row.get("Aerial Duels_Won", 0) or 0)
        - 1.5 * (row.get("Aerial Duels_Lost", 0) or 0)
        + 2.7 * (row.get("Performance_Tkl", 0) or 0)
        - 1.6 * (row.get("Challenges_Lost", 0) or 0)
        + 2.7 * (row.get("Performance_Int", 0) or 0)
        + 1.1 * (row.get("Unnamed: 20_level_0_Clr", row.get("Clr", 0)) or 0)
        + (10 - (5 * team_conc))
        + (row.get("Passes_Cmp", 0) or 0) / 9.0
        - (((row.get("Passes_Att", 0) or 0) - (row.get("Passes_Cmp", 0) or 0)) / 4.5)
        + (row.get("Unnamed: 23_level_0_KP", row.get("Pass Types_KP", 0)) or 0)
        + (row.get("Take-Ons_Succ", 0) or 0) * 2.5
        + 1.1 * (row.get("Blocks_Sh", 0) or 0)
        + 2.5 * (row.get("Performance_SoT", 0) or 0)
        + (row.get("Performance_Gls", 0) or 0) * 10
        + (row.get("Performance_Ast", 0) or 0) * 8
        - 5 * (row.get("Performance_CrdR", 0) or 0)
    )
    return round(score, 0)


def mid_score_calc(row):
    team_conc = row.get("goals_conceded", 0) or 0
    team_score = row.get("goals_scored", 0) or 0

    score = (
        1.7 * (row.get("Aerial Duels_Won", 0) or 0)
        + 2.6 * (row.get("Performance_Tkl", 0) or 0)
        + 2.5 * (row.get("Performance_Int", 0) or 0)
        + (4 - (2 * team_conc) + (2 * team_score))
        + (row.get("Passes_Cmp", 0) or 0) / 6.6
        - (((row.get("Passes_Att", 0) or 0) - (row.get("Passes_Cmp", 0) or 0)) / 3.2)
        + (row.get("Unnamed: 23_level_0_KP", row.get("Pass Types_KP", 0)) or 0)
        + (row.get("Take-Ons_Succ", 0) or 0) * 2.9
        + 2.2 * (row.get("Performance_SoT", 0) or 0)
        + (row.get("Performance_Gls", 0) or 0) * 10
        + (row.get("Performance_Ast", 0) or 0) * 8
        - 5 * (row.get("Performance_CrdR", 0) or 0)
    )
    return round(score, 0)


def fwd_score_calc(row):
    team_score = row.get("goals_scored", 0) or 0

    score = (
        1.4 * (row.get("Aerial Duels_Won", 0) or 0)
        + 2.6 * (row.get("Performance_Tkl", 0) or 0)
        + 2.7 * (row.get("Performance_Int", 0) or 0)
        + (3 * team_score)
        + (row.get("Passes_Cmp", 0) or 0) / 6.0
        + (row.get("Unnamed: 23_level_0_KP", row.get("Pass Types_KP", 0)) or 0)
        + (row.get("Take-Ons_Succ", 0) or 0) * 3.0
        + 3.0 * (row.get("Performance_SoT", 0) or 0)
        + (row.get("Performance_Gls", 0) or 0) * 10
        + (row.get("Performance_Ast", 0) or 0) * 8
        - 5 * (row.get("Performance_CrdR", 0) or 0)
    )
    return round(score, 0)


# =========================
#  HTML → TABLE HELPERS
# =========================

def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten MultiIndex columns the same style as before:
    ('Unnamed: 0_level_0', 'Player') -> 'Unnamed: 0_level_0_Player'
    ('Performance', 'Gls') -> 'Performance_Gls'
    etc.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            "_".join(str(x) for x in col).strip("_")
            for col in df.columns.values
        ]
    else:
        df.columns = [str(c) for c in df.columns]
    return df


def _is_goalkeeper_only_table(df: pd.DataFrame) -> bool:
    """Return True if table looks like GK-only (all positions 'G')."""
    pos_col = next((c for c in df.columns if "Pos" in c), None)
    if not pos_col:
        return False
    uniq = df[pos_col].dropna().astype(str).str.strip().unique()
    if len(uniq) > 0 and all(v == "G" for v in uniq):
        return True
    return False


def _find_player_column(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if "Player" in c:
            return c
    return None


def _find_pos_column(df: pd.DataFrame) -> str | None:
    # Sometimes 'Unnamed: 3_level_0_Pos', sometimes just 'Pos'
    for c in df.columns:
        if c.endswith("_Pos") or c == "Pos" or "Pos" in c:
            return c
    return None


def _build_team_df(tables: list[pd.DataFrame], team_label: str) -> pd.DataFrame:
    """
    Given a list of 6 tables for one team, merge them on Player
    and compute scores.
    """
    merged = None

    for raw_df in tables:
        df = _flatten_columns(raw_df.copy())

        player_col = _find_player_column(df)
        if not player_col:
            continue

        df = df.rename(columns={player_col: "Player"})

        pos_col = _find_pos_column(df)
        if pos_col:
            df = df.rename(columns={pos_col: "Pos"})

        # Drop obvious non-stat columns if present
        for drop_col in ["Rk"]:
            if drop_col in df.columns:
                df = df.drop(columns=[drop_col])

        # First table initializes 'merged'
        if merged is None:
            merged = df
        else:
            # Merge only new stat columns to avoid duplicate suffix issues
            new_cols = [c for c in df.columns if c not in merged.columns or c == "Player"]
            if "Player" in new_cols:
                new_cols = ["Player"] + [c for c in new_cols if c != "Player"]
            merged = merged.merge(df[new_cols], on="Player", how="left")

    if merged is None or merged.empty:
        raise ValueError(f"No valid player rows found for team {team_label}.")

    # Ensure we have Pos
    if "Pos" not in merged.columns:
        merged["Pos"] = "MID"

    # Set team-level goals scored / conceded
    # For now:
    #   - goals_scored = Performance_Gls (player's own goals)
    #   - goals_conceded = 0 (we can wire events later if needed)
    merged["goals_scored"] = merged.get("Performance_Gls", 0).fillna(0)
    merged["goals_conceded"] = 0

    # Normalize position + compute score
    merged["pos"] = merged["Pos"].apply(position_calcul)

    def compute_score(row):
        if row["pos"] == "FWD":
            return fwd_score_calc(row)
        elif row["pos"] == "MID":
            return mid_score_calc(row)
        elif row["pos"] == "DEF":
            return def_score_calc(row)
        else:
            return mid_score_calc(row)

    merged["score"] = merged.apply(compute_score, axis=1)

    merged["Team"] = team_label

    return merged[["Player", "Team", "pos", "score"]]


# =========================
#  PUBLIC ENTRYPOINT
# =========================

def calc_all_players_from_html(html_content: str) -> pd.DataFrame:
    """
    Main function to be called from Streamlit.

    - html_content: string of the full HTML of the match page (uploaded file)
    - Returns: DataFrame with columns [Player, Team, pos, score]
    """
    # Parse *all* tables with pandas
    all_tables = pd.read_html(html_content)

    # Filter to tables that have a Player column, skip GK-only tables
    player_tables = []
    for df in all_tables:
        df_flat = _flatten_columns(df.copy())
        player_col = _find_player_column(df_flat)
        if not player_col:
            continue
        if _is_goalkeeper_only_table(df_flat):
            continue
        # Keep the original (unflattened) df for merging; we re-flatten inside _build_team_df
        player_tables.append(df)

    if len(player_tables) < 2:
        raise ValueError(f"Could not find enough player stat tables. Found {len(player_tables)}.")

    # Hard-code: first half = home, second half = away
    # In FBref layout: usually 6 tables per team (Summary, Passing, Pass Types, Def Actions, Possession, Misc)
    half = len(player_tables) // 2
    home_tables = player_tables[:half]
    away_tables = player_tables[half:]

    if len(home_tables) == 0 or len(away_tables) == 0:
        raise ValueError("Could not split player tables into home and away teams.")

    home_df = _build_team_df(home_tables, "Home")
    away_df = _build_team_df(away_tables, "Away")

    combined = pd.concat([home_df, away_df], ignore_index=True)

    # Filter out Pedrinho as you had in your older code
    combined = combined[combined["Player"] != "Pedrinho"]

    combined["score"] = combined["score"].astype(int)

    return combined


# Optional CLI hook if you ever want to run this locally
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        df = calc_all_players_from_html(html)
        out = "match_output.csv" if len(sys.argv) < 3 else sys.argv[2]
        df.to_csv(out, index=False)
        print(f"✅ Saved results → {out}")
