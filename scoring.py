# scoring.py
# ==========================================================
#   FBref match-report HTML  ➜  merged per-team stats
#   ➜  fantasy scores (DEF/MID/FWD/GK)
# ==========================================================

import pandas as pd
from bs4 import BeautifulSoup

# ----------------------------------------------------------
# position helper
# ----------------------------------------------------------

def position_calcul(pos):
    """Normalize FBref position strings to FWD / MID / DEF / GK."""
    if pd.isna(pos):
        return "MID"

    pos = str(pos).strip()

    if len(pos) > 2:
        final_pos = pos.split(",")[0].strip()
    else:
        final_pos = pos

    # GK explicit handling
    if final_pos.upper().startswith("GK"):
        return "GK"

    if final_pos.endswith("W"):
        return "FWD"
    elif final_pos.endswith("M"):
        return "MID"
    elif final_pos.endswith("B"):
        return "DEF"
    else:
        return "MID"


# ----------------------------------------------------------
# safe getters for stats
# ----------------------------------------------------------

def _get(row: pd.Series, col: str, default: float = 0.0) -> float:
    """Safely pull a numeric stat from a row."""
    if col not in row.index:
        return default
    val = row[col]
    try:
        if pd.isna(val):
            return default
    except TypeError:
        pass
    try:
        return float(val)
    except Exception:
        return default


def _get_any(row: pd.Series, candidates, default: float = 0.0) -> float:
    """
    Try several possible column names for the same stat.
    Returns the first non-missing match.
    """
    for c in candidates:
        if c in row.index:
            v = _get(row, c, default=None)
            if v is not None:
                return v
    return default


# ----------------------------------------------------------
# Outfield scoring functions (your original logic)
# ----------------------------------------------------------

def def_score_calc(row: pd.Series) -> float:
    team_score = _get(row, "goals_scored", 0)
    team_conc = _get(row, "goals_conceded", 0)

    score = (
        1.9 * _get(row, "Aerial Duels_Won")
        - 1.5 * _get(row, "Aerial Duels_Lost")
        + 2.7 * _get(row, "Performance_Tkl")
        - 1.6 * _get(row, "Challenges_Lost")
        + 2.7 * _get(row, "Performance_Int")
        + 1.1 * _get(row, "Unnamed: 20_level_0_Clr")
        + (10 - (5 * team_conc))
        + (
            3
            - 1.2 * _get(row, "Carries_Dis")
            - 0.6 * (_get(row, "Performance_Fls") + _get(row, "Performance_Off"))
            - 3.5 * _get(row, "Performance_OG")
            - 5 * _get(row, "Unnamed: 21_level_0_Err")
        )
        + _get(row, "Passes_Cmp") / 9.0
        - ((_get(row, "Passes_Att") - _get(row, "Passes_Cmp")) / 4.5)
        + _get(row, "Unnamed: 23_level_0_KP")
        + 2.5 * _get(row, "Take-Ons_Succ")
        - 0.8 * (_get(row, "Take-Ons_Att") - _get(row, "Take-Ons_Succ"))
        + 1.1 * _get(row, "Blocks_Sh")
        + 1.5 * _get(row, "Unnamed: 23_level_0_KP")
        + 1.2 * _get(row, "Performance_Crs")
        + 2.5 * _get(row, "Performance_SoT")
        + ((_get(row, "Performance_Sh") - _get(row, "Performance_SoT")) / 2.0)
        + _get(row, "Unnamed: 5_level_0_Min") / 30.0
        + 10 * _get(row, "Performance_Gls")
        + 8 * _get(row, "Performance_Ast")
        - 5 * _get(row, "Performance_CrdR")
        - 5 * _get(row, "Performance_PKcon")
        - 5 * (_get(row, "Performance_PKatt") - _get(row, "Performance_PK"))
    )

    # PK won but not scored
    if _get(row, "Performance_PKwon") == 1 and _get(row, "Performance_PK") != 1:
        score += 6.4

    # early-sub clean sheet penalty
    if _get(row, "Unnamed: 5_level_0_Min") <= 45 and team_conc == 0:
        score -= 5

    return round(score, 0)


def mid_score_calc(row: pd.Series) -> float:
    team_score = _get(row, "goals_scored", 0)
    team_conc = _get(row, "goals_conceded", 0)

    score = (
        1.7 * _get(row, "Aerial Duels_Won")
        - 1.5 * _get(row, "Aerial Duels_Lost")
        + 2.6 * _get(row, "Performance_Tkl")
        - 1.2 * _get(row, "Challenges_Lost")
        + 2.5 * _get(row, "Performance_Int")
        + 1.1 * _get(row, "Unnamed: 20_level_0_Clr")
        + (4 - (2 * team_conc) + (2 * team_score))
        + (
            3
            - 1.1 * _get(row, "Carries_Dis")
            - 0.6 * (_get(row, "Performance_Fls") + _get(row, "Performance_Off"))
            - 3.3 * _get(row, "Performance_OG")
            - 5 * _get(row, "Unnamed: 21_level_0_Err")
        )
        + _get(row, "Passes_Cmp") / 6.6
        - ((_get(row, "Passes_Att") - _get(row, "Passes_Cmp")) / 3.2)
        + _get(row, "Unnamed: 23_level_0_KP")
        + 2.9 * _get(row, "Take-Ons_Succ")
        - 0.8 * (_get(row, "Take-Ons_Att") - _get(row, "Take-Ons_Succ"))
        + 1.1 * _get(row, "Blocks_Sh")
        + 1.5 * _get(row, "Unnamed: 23_level_0_KP")
        + 1.2 * _get(row, "Performance_Crs")
        + 2.2 * _get(row, "Performance_SoT")
        + ((_get(row, "Performance_Sh") - _get(row, "Performance_SoT")) / 4.0)
        + _get(row, "Unnamed: 5_level_0_Min") / 30.0
        + 10 * _get(row, "Performance_Gls")
        + 8 * _get(row, "Performance_Ast")
        - 5 * _get(row, "Performance_CrdR")
        - 5 * _get(row, "Performance_PKcon")
        - 5 * (_get(row, "Performance_PKatt") - _get(row, "Performance_PK"))
    )

    if _get(row, "Performance_PKwon") == 1 and _get(row, "Performance_PK") != 1:
        score += 6.4

    return round(score, 0)


def fwd_score_calc(row: pd.Series) -> float:
    team_score = _get(row, "goals_scored", 0)

    score = (
        1.4 * _get(row, "Aerial Duels_Won")
        - 0.4 * _get(row, "Aerial Duels_Lost")
        + 2.6 * _get(row, "Performance_Tkl")
        - 1.0 * _get(row, "Challenges_Lost")
        + 2.7 * _get(row, "Performance_Int")
        + 0.8 * _get(row, "Unnamed: 20_level_0_Clr")
        + (3 * team_score)
        + (
            5
            - 0.9 * _get(row, "Carries_Dis")
            - 0.5 * (_get(row, "Performance_Fls") + _get(row, "Performance_Off"))
            - 3.0 * _get(row, "Performance_OG")
            - 5 * _get(row, "Unnamed: 21_level_0_Err")
        )
        + _get(row, "Passes_Cmp") / 6.0
        - ((_get(row, "Passes_Att") - _get(row, "Passes_Cmp")) / 8.0)
        + _get(row, "Unnamed: 23_level_0_KP")
        + 3.0 * _get(row, "Take-Ons_Succ")
        - 1.0 * (_get(row, "Take-Ons_Att") - _get(row, "Take-Ons_Succ"))
        + 0.8 * _get(row, "Blocks_Sh")
        + 1.5 * _get(row, "Unnamed: 23_level_0_KP")
        + 1.2 * _get(row, "Performance_Crs")
        + 3.0 * _get(row, "Performance_SoT")
        + ((_get(row, "Performance_Sh") - _get(row, "Performance_SoT")) / 3.0)
        + _get(row, "Unnamed: 5_level_0_Min") / 30.0
        + 10 * _get(row, "Performance_Gls")
        + 8 * _get(row, "Performance_Ast")
        - 5 * _get(row, "Performance_CrdR")
        - 5 * _get(row, "Performance_PKcon")
        - 5 * (_get(row, "Performance_PKatt") - _get(row, "Performance_PK"))
    )

    if _get(row, "Performance_PKwon") == 1 and _get(row, "Performance_PK") != 1:
        score += 6.4

    return round(score, 0)


# ----------------------------------------------------------
# NEW GK scoring – EXACTLY as in your screenshot
# ----------------------------------------------------------

def gk_score_calc(row: pd.Series) -> float:

    GA = _get_any(row, ["Shot Stopping_GA", "GA"], 0)
    Saves = _get_any(row, ["Shot Stopping_Saves", "Saves"], 0)
    Cmp = _get_any(row, ["Launched_Cmp"], 0)
    Stp = _get_any(row, ["Crosses_Stp"], 0)
    OPA = _get_any(row, ["Sweeper_#OPA", "#OPA"], 0)

    # Goal concession penalty
    if GA == 0:
        ga_penalty = 0
    elif GA == 1:
        ga_penalty = -5
    else:
        ga_penalty = -5 - 3 * (GA - 1)

    # Base scoring rule
    score = (
        17
        + 2.5 * Saves   # shot-stopping reward
        + 0.5 * Cmp     # long passes completed
        + 1.0 * Stp     # crosses stopped
        + 1.0 * OPA     # sweeper actions
        + ga_penalty    # goals conceded penalty
    )
    if GA == 0:
        score += 2
        
    return round(score, 0)


# ----------------------------------------------------------
# HTML → per-team merged DataFrames
# ----------------------------------------------------------

def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            "_".join([str(x) for x in col if str(x) != "nan"]).strip("_")
            for col in df.columns
        ]
    else:
        df.columns = [str(c) for c in df.columns]
    return df


def _standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename FBref columns to the names used by your original outfield formula.
    GK columns are left with their natural flattened names
    (Shot Stopping_GA, Launched_Cmp, Crosses_Stp, Sweeper_#OPA, etc.).
    """
    rename_map = {
        # core performance
        "Player": "Player",
        "Pos": "Pos",
        "Min": "Unnamed: 5_level_0_Min",
        "Gls": "Performance_Gls",
        "Ast": "Performance_Ast",
        "PK": "Performance_PK",
        "PKatt": "Performance_PKatt",
        "Sh": "Performance_Sh",
        "SoT": "Performance_SoT",
        "CrdY": "Performance_CrdY",
        "CrdR": "Performance_CrdR",
        "Tkl": "Performance_Tkl",
        "Int": "Performance_Int",
        # passing
        "Cmp": "Passes_Cmp",
        "Att": "Passes_Att",      # from the passing table
        "KP": "Unnamed: 23_level_0_KP",
        "Crs": "Performance_Crs",
        # possession & misc
        "Dis": "Carries_Dis",
        "Won": "Aerial Duels_Won",
        "Lost": "Aerial Duels_Lost",
        "Fls": "Performance_Fls",
        "Off": "Performance_Off",
        "OG": "Performance_OG",
        "PKcon": "Performance_PKcon",
        "PKwon": "Performance_PKwon",
        "Err": "Unnamed: 21_level_0_Err",
        "Blocks": "Blocks_Sh",
        # NOTE: no special renames for GK columns – we use their
        # flattened names directly in gk_score_calc.
    }

    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)
    return df


def _merge_team_tables(team_dfs):
    """Merge the 6 outfield tables + GK table(s) for one team on Player."""
    merged = None
    for df in team_dfs:
        df = _flatten_columns(df.copy())

        # identify player column
        player_col = next((c for c in df.columns if "player" in c.lower()), None)
        if not player_col:
            continue
        df = df.rename(columns={player_col: "Player"})

        # drop total rows such as "16 Players"
        df = df[~df["Player"].astype(str).str.contains("Players")]

        # standardise outfield column names
        df = _standardise_columns(df)

        if merged is None:
            merged = df
        else:
            # avoid duplicate stat columns when merging
            dup_cols = [c for c in df.columns if c != "Player" and c in merged.columns]
            if dup_cols:
                df = df.drop(columns=dup_cols)
            merged = merged.merge(df, on="Player", how="left")

    if merged is None:
        return pd.DataFrame()

    merged.reset_index(drop=True, inplace=True)
    return merged


def _extract_team_tables_from_html(html_text: str):
    """
    Returns dict: team_name -> list of DataFrames for that team's tabs.
    Includes both "Player Stats Table" and "Goalkeeper Stats".
    """
    soup = BeautifulSoup(html_text, "html.parser")
    tables = soup.find_all("table")
    dfs = pd.read_html(html_text)

    team_to_dfs = {}
    idx = 0
    for t in tables:
        caption = t.find("caption")
        if caption:
            text = caption.get_text()

            if "Player Stats Table" in text:
                team_name = text.split(" Player Stats")[0].strip()
                df = dfs[idx]
                team_to_dfs.setdefault(team_name, []).append(df)

            elif "Goalkeeper Stats" in text:
                team_name = text.split(" Goalkeeper Stats")[0].strip()
                df = dfs[idx]
                team_to_dfs.setdefault(team_name, []).append(df)

        idx += 1

    return team_to_dfs


# ----------------------------------------------------------
# MAIN ENTRY POINT used by Streamlit
# ----------------------------------------------------------

def calc_all_players_from_html(html_text: str) -> pd.DataFrame:
    """
    Main function:
      - Read FBref match-report HTML (already uploaded),
      - Merge all per-team tables (outfield + GK),
      - Compute scores.
    """
    team_tables = _extract_team_tables_from_html(html_text)
    if len(team_tables) == 0:
        raise ValueError("No team player stats tables found in the HTML.")

    # Build merged table for each team
    team_frames = {}
    for team, dfs in team_tables.items():
        team_frames[team] = _merge_team_tables(dfs)

    if len(team_frames) == 0:
        raise ValueError("Could not create any team dataframes from HTML.")

    teams = list(team_frames.keys())

    # ---- infer goals scored per team from Gls column ----
    if len(teams) >= 1:
        t1 = teams[0]
        df1 = team_frames[t1]
        g1 = _get(df1.sum(numeric_only=True), "Performance_Gls", 0)
    else:
        raise ValueError("No first team data found.")

    if len(teams) >= 2:
        t2 = teams[1]
        df2 = team_frames[t2]
        g2 = _get(df2.sum(numeric_only=True), "Performance_Gls", 0)
    else:
        t2 = None
        df2 = pd.DataFrame()
        g2 = 0

    # attach goals_scored / goals_conceded and team label (for outfield logic)
    if len(teams) >= 1:
        team_frames[t1]["goals_scored"] = g1
        team_frames[t1]["goals_conceded"] = g2
        team_frames[t1]["Team"] = "Home"

    if len(teams) >= 2:
        team_frames[t2]["goals_scored"] = g2
        team_frames[t2]["goals_conceded"] = g1
        team_frames[t2]["Team"] = "Away"

    # combine both teams
    combined_full = pd.concat(team_frames.values(), ignore_index=True)

    # ------------------------------------------------------
    #  Robust detection of the Position column
    # ------------------------------------------------------
    if "Pos" not in combined_full.columns:
        pos_candidate = None
        for c in combined_full.columns:
            cname = str(c).lower()
            if "pos" in cname and "xg" not in cname and "pass" not in cname:
                pos_candidate = c
                break

        if pos_candidate is not None:
            combined_full = combined_full.rename(columns={pos_candidate: "Pos"})
        else:
            combined_full["Pos"] = "UNK"

    # ------------------------------------------------------
    #  Classify into FWD / MID / DEF / GK and compute scores
    # ------------------------------------------------------
    combined_full["pos"] = combined_full["Pos"].apply(position_calcul)

    def _apply_score(row):
        if row["pos"] == "FWD":
            return fwd_score_calc(row)
        elif row["pos"] == "MID":
            return mid_score_calc(row)
        elif row["pos"] == "DEF":
            return def_score_calc(row)
        elif row["pos"] == "GK":
            return gk_score_calc(row)
        else:
            # fallback – treat unknown like MID
            return mid_score_calc(row)

    combined_full["score"] = combined_full.apply(_apply_score, axis=1)

    # Slim result for the UI
    result = combined_full[["Player", "Team", "pos", "score"]].copy()
    return result


# ----------------------------------------------------------
# DEBUG HELPER – score breakdown for one player
# ----------------------------------------------------------

def debug_player_components(full_df: pd.DataFrame, player_name: str) -> dict:
    """
    Return a dict of the stats used in scoring for a given player,
    plus their position bucket and final score.
    """
    row = full_df[full_df["Player"] == player_name]
    if row.empty:
        raise ValueError(f"No player named '{player_name}' found.")
    row = row.iloc[0]

    pos_bucket = position_calcul(row.get("Pos", "MID"))

    # All stats your formulas actually use
    stats_used = [
        "Aerial Duels_Won", "Aerial Duels_Lost",
        "Performance_Tkl", "Challenges_Lost", "Performance_Int",
        "Unnamed: 20_level_0_Clr", "Carries_Dis",
        "Performance_Fls", "Performance_Off", "Performance_OG",
        "Unnamed: 21_level_0_Err", "Passes_Cmp", "Passes_Att",
        "Unnamed: 23_level_0_KP", "Take-Ons_Att", "Take-Ons_Succ",
        "Blocks_Sh", "Performance_Crs", "Performance_SoT",
        "Performance_Sh", "Unnamed: 5_level_0_Min",
        "Performance_Gls", "Performance_Ast",
        "Performance_CrdR", "Performance_PKcon",
        "Performance_PKatt", "Performance_PK",
        "Performance_PKwon", "goals_scored", "goals_conceded",
    ]

    data = {stat: _get(row, stat, 0) for stat in stats_used}

    if pos_bucket == "FWD":
        score = fwd_score_calc(row)
    elif pos_bucket == "MID":
        score = mid_score_calc(row)
    else:  # DEF is the case for Inácio
        score = def_score_calc(row)

    data["pos_bucket"] = pos_bucket
    data["final_score"] = score
    return data
