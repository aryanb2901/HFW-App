# scoring.py
# ==========================================================
#   FBref match-report HTML  ➜  merged per-team stats
#   ➜  fantasy scores (DEF/MID/FWD) + separate GK scoring
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
        return "UNK"


# ----------------------------------------------------------
# safe getters
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
    """Try several possible column names for the same stat."""
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
# GK scoring (your spec)
# ----------------------------------------------------------

def gk_score_calc(row: pd.Series) -> float:
    """
    Goalkeeper scoring:

      Minutes:             +0.1 × minutes
      Clean sheet (>=60m & 0 GA): +12
      Goals conceded:      5 - 5 × goals_conceded
      Saves:               +3 × saves
      Penalties saved:     +15 × pens_saved
      Penalties conceded:  -5 × pens_conceded
      Crosses claimed:     +1 × crosses
      Sweeper actions:     +1.5 × sweeper_actions
      Error leading shot:  -3 × errors_shot (not separate in FBref; treated as 0)
      Error leading goal:  -7.5 × errors_goal
      Yellow card:         -3 × yellow_cards
      Red card:            -10 × red_cards
      Own goal:            -5 × own_goals

      Min floor: 5 pts.
    """
    minutes = _get(row, "Unnamed: 5_level_0_Min", 0)
    goals_conceded = _get(row, "goals_conceded", 0)

    saves = _get_any(row, ["Saves", "Shot Stopping_Saves"], 0)

    pens_saved = _get_any(row, ["PKsv", "PK Saved", "PK Saves"], 0)
    pens_conceded = _get_any(row, ["Performance_PKcon", "PKcon", "PK Conceded"], 0)

    crosses = _get_any(row, ["Crosses_Stopped", "Crosses_Stp", "Stp"], 0)

    sweeper_actions = _get_any(row, ["#OPA", "Sweeper_#OPA"], 0)

    errors_shot = 0
    errors_goal = _get_any(row, ["Unnamed: 21_level_0_Err", "Err"], 0)

    yellow_cards = _get(row, "Performance_CrdY", 0)
    red_cards = _get(row, "Performance_CrdR", 0)
    own_goals = _get(row, "Performance_OG", 0)

    score = 0.0

    score += 0.1 * minutes

    if minutes >= 60 and goals_conceded == 0:
        score += 12

    score += 5 - (5 * goals_conceded)
    score += 3 * saves
    score += 15 * pens_saved
    score += -5 * pens_conceded
    score += 1 * crosses
    score += 1.5 * sweeper_actions
    score += -3 * errors_shot
    score += -7.5 * errors_goal
    score += -3 * yellow_cards
    score += -10 * red_cards
    score += -5 * own_goals

    score = max(score, 5)
    return round(score, 0)


# ----------------------------------------------------------
# HTML → per-team merged DataFrames (OUTFIELD ONLY)
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


def _standardise_outfield_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename FBref columns to the names used by your original formula
    (OUTFIELD ONLY – no GK fields here).
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
        "Att": "Passes_Att",
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
    }

    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)
    return df


def _merge_outfield_team_tables(team_dfs):
    """Merge the 6 outfield tables for one team on Player."""
    merged = None
    for df in team_dfs:
        df = _flatten_columns(df.copy())

        player_col = next((c for c in df.columns if "player" in c.lower()), None)
        if not player_col:
            continue
        df = df.rename(columns={player_col: "Player"})

        df = df[~df["Player"].astype(str).str.contains("Players")]

        df = _standardise_outfield_columns(df)

        if merged is None:
            merged = df
        else:
            dup_cols = [c for c in df.columns if c != "Player" and c in merged.columns]
            if dup_cols:
                df = df.drop(columns=dup_cols)
            merged = merged.merge(df, on="Player", how="left")

    if merged is None:
        return pd.DataFrame()

    merged.reset_index(drop=True, inplace=True)
    return merged


def _extract_outfield_team_tables_from_html(html_text: str):
    """
    Returns dict: team_name -> list of DataFrames for that team's
    *outfield* "Player Stats Table" tabs only.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    tables = soup.find_all("table")
    dfs = pd.read_html(html_text)

    team_to_dfs = {}
    idx = 0
    for t in tables:
        caption = t.find("caption")
        if caption and "Player Stats Table" in caption.get_text():
            text = caption.get_text()
            team_name = text.split(" Player Stats")[0].strip()
            df = dfs[idx]
            team_to_dfs.setdefault(team_name, []).append(df)
        idx += 1

    return team_to_dfs


# ----------------------------------------------------------
# GK tables parsed separately
# ----------------------------------------------------------

def _extract_gk_tables_from_html(html_text: str):
    """
    Returns dict: team_name -> GK DataFrame (one row per GK).
    """
    soup = BeautifulSoup(html_text, "html.parser")
    tables = soup.find_all("table")
    dfs = pd.read_html(html_text)

    team_to_gk_df = {}
    idx = 0
    for t in tables:
        caption = t.find("caption")
        if caption and "Goalkeeper Stats" in caption.get_text():
            text = caption.get_text()
            team_name = text.split(" Goalkeeper Stats")[0].strip()
            df = dfs[idx]
            df = _flatten_columns(df.copy())

            # identify Player col
            player_col = next((c for c in df.columns if "player" in c.lower()), None)
            if not player_col:
                idx += 1
                continue
            df = df.rename(columns={player_col: "Player"})

            # drop totals
            df = df[~df["Player"].astype(str).str.contains("Players")]

            # ---- key part: handle flattened multiindex names ----
            rename_map = {
                # minutes
                "Min": "Unnamed: 5_level_0_Min",

                # goals against & saves come under "Shot Stopping"
                "Shot Stopping_GA": "GA",
                "GA": "GA",
                "Shot Stopping_Saves": "Saves",
                "Saves": "Saves",

                # crosses stopped under "Crosses"
                "Crosses_Stp": "Crosses_Stopped",
                "Stp": "Crosses_Stopped",

                # sweeper actions under "Sweeper"
                "Sweeper_#OPA": "#OPA",
                "#OPA": "#OPA",

                # cards / OG / errors if they ever appear here
                "CrdY": "Performance_CrdY",
                "CrdR": "Performance_CrdR",
                "OG": "Performance_OG",
                "Err": "Unnamed: 21_level_0_Err",
            }

            rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
            df = df.rename(columns=rename_map)

            team_to_gk_df[team_name] = df

        idx += 1

    return team_to_gk_df

# ----------------------------------------------------------
# MAIN ENTRY POINT used by Streamlit
# ----------------------------------------------------------

def calc_all_players_from_html(html_text: str) -> pd.DataFrame:
    """
    Main function:
      - Read FBref match-report HTML,
      - Build outfield scores with original logic,
      - Build GK scores separately,
      - Return combined table.
    """

    # ---------- OUTFIELD PLAYERS ----------
    outfield_team_tables = _extract_outfield_team_tables_from_html(html_text)
    if len(outfield_team_tables) == 0:
        raise ValueError("No outfield team player stats tables found in the HTML.")

    team_frames = {}
    for team, dfs in outfield_team_tables.items():
        team_frames[team] = _merge_outfield_team_tables(dfs)

    if len(team_frames) == 0:
        raise ValueError("Could not create any outfield dataframes from HTML.")

    teams = list(team_frames.keys())

    # infer goals scored per team from Gls column
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

    if len(teams) >= 1:
        team_frames[t1]["goals_scored"] = g1
        team_frames[t1]["goals_conceded"] = g2
        team_frames[t1]["Team"] = "Home"

    if len(teams) >= 2:
        team_frames[t2]["goals_scored"] = g2
        team_frames[t2]["goals_conceded"] = g1
        team_frames[t2]["Team"] = "Away"

    combined_full = pd.concat(team_frames.values(), ignore_index=True)

    # robust detection of Pos
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

    combined_full["pos"] = combined_full["Pos"].apply(position_calcul)

    def _apply_outfield_score(row):
        if row["pos"] == "FWD":
            return fwd_score_calc(row)
        elif row["pos"] == "MID":
            return mid_score_calc(row)
        else:
            return def_score_calc(row)

    # Only apply outfield scoring to non-GKs
    mask_gk = combined_full["pos"] == "GK"
    combined_full.loc[~mask_gk, "score"] = combined_full[~mask_gk].apply(
        _apply_outfield_score, axis=1
    )

    outfield_result = combined_full.loc[~mask_gk, ["Player", "Team", "pos", "score"]]

    # ---------- GOALKEEPERS ----------
    gk_tables = _extract_gk_tables_from_html(html_text)

    gk_rows = []
    for team_name, gk_df in gk_tables.items():
        # Map team_name -> Team label & GA from g1/g2
        if team_name == t1:
            team_label = "Home"
            goals_conceded = g2
        elif t2 is not None and team_name == t2:
            team_label = "Away"
            goals_conceded = g1
        else:
            # In weird cases, just default
            team_label = "Home"
            goals_conceded = 0

        for _, row in gk_df.iterrows():
            row = row.copy()
            row["Team"] = team_label
            row["goals_conceded"] = goals_conceded
            row["pos"] = "GK"
            score = gk_score_calc(row)
            gk_rows.append(
                {
                    "Player": row["Player"],
                    "Team": team_label,
                    "pos": "GK",
                    "score": score,
                }
            )

    gk_result = pd.DataFrame(gk_rows) if gk_rows else pd.DataFrame(
        columns=["Player", "Team", "pos", "score"]
    )

    # ---------- FINAL COMBINED ----------
    final = pd.concat([outfield_result, gk_result], ignore_index=True)

    return final


# ----------------------------------------------------------
# DEBUG helper (optional)
# ----------------------------------------------------------

def debug_player_components(full_df: pd.DataFrame, player_name: str) -> dict:
    """
    For a given player row in the *full* DataFrame (with all columns),
    return the stats used and the final score.
    """
    row = full_df[full_df["Player"] == player_name]
    if row.empty:
        raise ValueError(f"No player named '{player_name}' found.")
    row = row.iloc[0]

    pos_bucket = position_calcul(row.get("Pos", "MID"))

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
        "Saves", "Crosses_Stopped", "#OPA",
    ]

    data = {stat: _get(row, stat, 0) for stat in stats_used}

    if pos_bucket == "FWD":
        score = fwd_score_calc(row)
    elif pos_bucket == "MID":
        score = mid_score_calc(row)
    elif pos_bucket == "DEF":
        score = def_score_calc(row)
    else:
        score = gk_score_calc(row)

    data["pos_bucket"] = pos_bucket
    data["final_score"] = score
    return data
