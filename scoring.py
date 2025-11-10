import pandas as pd
from bs4 import BeautifulSoup

# -------------------------------------------------
# Helpers for columns / positions / safe numbers
# -------------------------------------------------

def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns like ('Performance','Tkl') -> 'Performance_Tkl'."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            "_".join([str(c) for c in col if str(c) != "nan"]).strip("_")
            for col in df.columns
        ]
    else:
        df.columns = [str(c) for c in df.columns]
    return df


def _normalise_core_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure we have 'Player' and 'Pos' columns with consistent names."""
    df = _flatten_columns(df)

    # Find Player column
    player_col = None
    for c in df.columns:
        if "player" in str(c).lower():
            player_col = c
            break
    if player_col is None:
        raise ValueError("Could not find a 'Player' column in a team table.")
    if player_col != "Player":
        df = df.rename(columns={player_col: "Player"})

    # Find Pos column (if missing, create default)
    pos_col = None
    for c in df.columns:
        if str(c).lower() in ("pos", "position"):
            pos_col = c
            break
    if pos_col and pos_col != "Pos":
        df = df.rename(columns={pos_col: "Pos"})
    elif pos_col is None:
        df["Pos"] = ""

    return df


def position_calcul(pos):
    """Collapse detailed positions into FWD / MID / DEF buckets."""
    s = str(pos).split(",")[0].strip()
    if s.endswith("W"):
        return "FWD"
    if s.endswith("M"):
        return "MID"
    if s.endswith("B"):
        return "DEF"
    return "MID"  # reasonable default


def _get(row: pd.Series, col: str, default: float = 0.0) -> float:
    """Safely pull a numeric stat from a row, without ever calling .fillna on scalars."""
    if col in row.index:
        val = row[col]
    else:
        return default

    try:
        # handle NaN
        if pd.isna(val):
            return default
    except TypeError:
        # non-numeric / non-NaN, we’ll just try float()
        pass

    try:
        return float(val)
    except Exception:
        return default


# -------------------------------------------------
# Scoring functions (FWD / MID / DEF)
# -------------------------------------------------

def def_score_calc(row: pd.Series) -> float:
    team_conc = _get(row, "goals_conceded", 0)
    score = (
        1.9 * _get(row, "Aerial Duels_Won")
        - 1.5 * _get(row, "Aerial Duels_Lost")
        + 2.7 * _get(row, "Performance_Tkl")
        - 1.6 * _get(row, "Challenges_Lost")
        + 2.7 * _get(row, "Performance_Int")
        + 1.1 * _get(row, "Unnamed: 20_level_0_Clr")
        + (10 - (5 * team_conc))
        + _get(row, "Passes_Cmp") / 9.0
        - ((_get(row, "Passes_Att") - _get(row, "Passes_Cmp")) / 4.5)
        + _get(row, "Unnamed: 23_level_0_KP")
        + 2.5 * _get(row, "Take-Ons_Succ")
        + 1.1 * _get(row, "Blocks_Sh")
        + 2.5 * _get(row, "Performance_SoT")
        + 10 * _get(row, "Performance_Gls")
        + 8 * _get(row, "Performance_Ast")
        - 5 * _get(row, "Performance_CrdR")
    )
    return round(score, 0)


def mid_score_calc(row: pd.Series) -> float:
    team_conc = _get(row, "goals_conceded", 0)
    team_score = _get(row, "goals_scored", 0)
    score = (
        1.7 * _get(row, "Aerial Duels_Won")
        + 2.6 * _get(row, "Performance_Tkl")
        + 2.5 * _get(row, "Performance_Int")
        + (4 - (2 * team_conc) + (2 * team_score))
        + _get(row, "Passes_Cmp") / 6.6
        - ((_get(row, "Passes_Att") - _get(row, "Passes_Cmp")) / 3.2)
        + _get(row, "Unnamed: 23_level_0_KP")
        + 2.9 * _get(row, "Take-Ons_Succ")
        + 2.2 * _get(row, "Performance_SoT")
        + 10 * _get(row, "Performance_Gls")
        + 8 * _get(row, "Performance_Ast")
        - 5 * _get(row, "Performance_CrdR")
    )
    return round(score, 0)


def fwd_score_calc(row: pd.Series) -> float:
    team_score = _get(row, "goals_scored", 0)
    score = (
        1.4 * _get(row, "Aerial Duels_Won")
        + 2.6 * _get(row, "Performance_Tkl")
        + 2.7 * _get(row, "Performance_Int")
        + 3 * team_score
        + _get(row, "Passes_Cmp") / 6.0
        + _get(row, "Unnamed: 23_level_0_KP")
        + 3.0 * _get(row, "Take-Ons_Succ")
        + 3.0 * _get(row, "Performance_SoT")
        + 10 * _get(row, "Performance_Gls")
        + 8 * _get(row, "Performance_Ast")
        - 5 * _get(row, "Performance_CrdR")
    )
    return round(score, 0)


# -------------------------------------------------
# HTML parsing & merging logic
# -------------------------------------------------

def _extract_team_tables(html: str):
    """
    Find all 'Player Stats Table' tables in the HTML and group them by team name.
    This will pick up:
      - Summary
      - Shots
      - Pass types
      - Defensive actions
      - Possession
      - Misc stats
    for each team.
    """
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    teams = {}  # {team_name: [df1, df2, ...]}

    for tbl in tables:
        caption = tbl.find("caption")
        if not caption:
            continue

        cap_text = caption.get_text(strip=True)
        if "Player Stats Table" not in cap_text:
            continue

        # Example caption: "Liverpool Player Stats Table"
        # or "Liverpool Player Stats Table – Defensive Actions"
        team_name = cap_text.split("Player Stats Table")[0].strip()

        df = pd.read_html(str(tbl))[0]
        teams.setdefault(team_name, []).append(df)

    if not teams:
        raise ValueError("Could not find any 'Player Stats Table' in the HTML.")

    return teams


def _merge_team_tables(dfs_for_team):
    """
    Given the list of DataFrames for one team (summary, passing, etc),
    normalise them and outer-merge on Player + Pos.
    """
    merged = None
    for df in dfs_for_team:
        df = _normalise_core_columns(df)

        # Ensure Player + Pos are first
        other_cols = [c for c in df.columns if c not in ("Player", "Pos")]
        df = df[["Player", "Pos"] + other_cols]

        if merged is None:
            merged = df
        else:
            merged = pd.merge(
                merged,
                df,
                on=["Player", "Pos"],
                how="outer",
                suffixes=("", "_dup"),
            )
            # Drop any duplicate columns produced by suffixes
            dup_cols = [c for c in merged.columns if c.endswith("_dup")]
            if dup_cols:
                merged = merged.drop(columns=dup_cols)

    return merged


# -------------------------------------------------
# Public function used by Streamlit
# -------------------------------------------------

def calc_all_players_from_html(html_content: str) -> pd.DataFrame:
    """
    Main entry: given the raw HTML (string) for a match report,
    return a DataFrame with Player, Team, pos, score.
    """
    teams_dict = _extract_team_tables(html_content)

    # Take first two distinct teams we find (home & away)
    team_names = list(teams_dict.keys())[:2]
    if len(team_names) < 1:
        raise ValueError("Did not find enough teams in the HTML.")

    team_dfs = []
    for idx, tname in enumerate(team_names):
        merged = _merge_team_tables(teams_dict[tname])
        merged["Team"] = "Home" if idx == 0 else "Away"
        team_dfs.append(merged)

    combined = pd.concat(team_dfs, ignore_index=True)

    # Position bucket
    combined["pos"] = combined["Pos"].apply(position_calcul)

    # Compute fantasy score
    def _compute(row):
        if row["pos"] == "FWD":
            return fwd_score_calc(row)
        elif row["pos"] == "MID":
            return mid_score_calc(row)
        else:
            return def_score_calc(row)

    combined["score"] = combined.apply(_compute, axis=1)

    # Final tidy output
    return combined[["Player", "Team", "pos", "score"]]
