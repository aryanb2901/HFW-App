# scoring.py
# ==========================================================
#   FBref match-report HTML  ➜  merged per-team stats
#   ➜  fantasy scores (DEF/MID/FWD) with original formula
#   ➜  goalkeeper scoring per latest scheme (image snippet)
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

    # FBref often lists like "CM,RM" etc.
    final_pos = pos.split(",")[0].strip() if len(pos) > 2 else pos

    if final_pos == "GK":
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
# safe getter for stats
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


# ----------------------------------------------------------
# full scoring functions (original outfield logic)
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

    if _get(row, "Performance_PKwon") == 1 and _get(row, "Performance_PK") != 1:
        score += 6.4

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
# NEW: Goalkeeper scoring (from your code image)
# ----------------------------------------------------------

def gk_score_calc(row: pd.Series) -> float:
    """
    Uses flattened FBref GK columns:
      - Shot Stopping_GA
      - Shot Stopping_Saves
      - Launched_Cmp
      - Crosses_Stp
      - Sweeper_#OPA
    Rule:
      base 17
      + 2.5*Saves
      + 1.5*Launched_Cmp
      + 1.0*Crosses_Stp
      + 1.0*#OPA
      + GA penalty: 0 (GA=0), -5 (GA=1), -5-3*(GA-1) (GA>=2)
      + clean sheet bonus +2 if GA=0
    Rounded to nearest integer.
    """
    GA = _get(row, "Shot Stopping_GA", 0)
    Saves = _get(row, "Shot Stopping_Saves", 0)
    Cmp = _get(row, "Launched_Cmp", 0)
    Stp = _get(row, "Crosses_Stp", 0)
    OPA = _get(row, "Sweeper_#OPA", 0)

    # GA penalty
    if GA == 0:
        ga_penalty = 0
    elif GA == 1:
        ga_penalty = -5
    else:
        ga_penalty = -5 - (3 * (GA - 1))

    score = (
        17
        + 2.5 * Saves
        + 1.5 * Cmp
        + 1.0 * Stp
        + 1.0 * OPA
        + ga_penalty
    )

    # clean sheet bonus
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


def _standardise_outfield_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename FBref columns to the names used by your original formula (outfield only)."""
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
    }
    # only rename columns that exist
    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    return df.rename(columns=rename_map)


def _merge_team_tables_outfield(team_dfs):
    """Merge the 6 OUTFIELD tables for one team on Player."""
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

        # standardise column names (outfield)
        df = _standardise_outfield_columns(df)

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
    Returns:
      - of_map: dict(team_name -> list of DataFrames for that team's OUTFIELD tabs)
      - gk_map: dict(team_name -> list of GK DataFrames (usually 1 row))
    """
    soup = BeautifulSoup(html_text, "html.parser")
    tables = soup.find_all("table")
    all_dfs = pd.read_html(html_text)

    of_map = {}
    gk_map = {}

    idx = 0
    for t in tables:
        caption = t.find("caption")
        cap = caption.get_text().strip() if caption else ""
        is_outfield = "Player Stats Table" in cap
        is_goalkeeper = ("Goalkeeper Stats" in cap) or ("Goalkeeping" in cap)

        # team name is the caption prefix before the descriptor
        team_name = None
        if is_outfield:
            team_name = cap.split(" Player Stats")[0].strip()
        elif is_goalkeeper:
            team_name = cap.split(" Goalkeeper Stats")[0].strip()
            if team_name == cap:  # fallback if caption format differs
                team_name = cap.split(" Goalkeeping")[0].strip()

        if team_name:
            df = all_dfs[idx]
            if is_outfield:
                of_map.setdefault(team_name, []).append(df)
            elif is_goalkeeper:
                gk_map.setdefault(team_name, []).append(df)

        idx += 1

    return of_map, gk_map


# ----------------------------------------------------------
# MAIN ENTRY POINT used by Streamlit
# ----------------------------------------------------------

def calc_all_players_from_html(html_text: str) -> pd.DataFrame:
    """
    Main function:
      - Read FBref match-report HTML (already uploaded),
      - Merge all per-team OUTFIELD tables,
      - Attach GK table rows (Pos='GK'),
      - Compute scores (outfield + GK).
    """
    of_map, gk_map = _extract_team_tables_from_html(html_text)
    if len(of_map) == 0 and len(gk_map) == 0:
        raise ValueError("No team player or goalkeeper tables found in the HTML.")

    # Build merged table for each team (outfield)
    team_frames = {}
    for team, dfs in of_map.items():
        team_frames[team] = _merge_team_tables_outfield(dfs)

    # Append GK rows (keep as their own rows, Pos='GK')
    for team, gk_dfs in gk_map.items():
        # concatenate all GK rows for that team (typically 1)
        gk_rows = []
        for gk_df in gk_dfs:
            df = _flatten_columns(gk_df.copy())
            player_col = next((c for c in df.columns if "player" in c.lower()), None)
            if not player_col:
                continue
            df = df.rename(columns={player_col: "Player"})
            df = df[~df["Player"].astype(str).str.contains("Players")]
            df["Pos"] = "GK"
            gk_rows.append(df)
        if gk_rows:
            gk_block = pd.concat(gk_rows, ignore_index=True)
            if team in team_frames and not team_frames[team].empty:
                team_frames[team] = pd.concat([team_frames[team], gk_block], ignore_index=True)
            else:
                # Team with only GK table (edge case)
                team_frames[team] = gk_block

    if len(team_frames) == 0:
        raise ValueError("Could not create any team dataframes from HTML.")

    teams = list(team_frames.keys())

    # ---- infer goals scored per team from outfield Gls (keeps original formulas intact) ----
    def _team_goals(df):
        if df is None or df.empty:
            return 0
        # outfield merged has 'Performance_Gls' after standardization
        return _get(df.sum(numeric_only=True), "Performance_Gls", 0)

    if len(teams) >= 1:
        t1 = teams[0]
        # split GK vs outfield to compute goals from outfield only
        df1_out = team_frames[t1][team_frames[t1].get("Pos", "").ne("GK")]
        g1 = _team_goals(df1_out)
    else:
        raise ValueError("No first team data found.")

    if len(teams) >= 2:
        t2 = teams[1]
        df2_out = team_frames[t2][team_frames[t2].get("Pos", "").ne("GK")]
        g2 = _team_goals(df2_out)
    else:
        t2 = None
        g2 = 0

    # attach goals_scored / goals_conceded and team label
    if len(teams) >= 1:
        team_frames[t1]["goals_scored"] = g1
        team_frames[t1]["goals_conceded"] = g2
        team_frames[t1]["Team"] = "Home"

    if t2 is not None:
        team_frames[t2]["goals_scored"] = g2
        team_frames[t2]["goals_conceded"] = g1
        team_frames[t2]["Team"] = "Away"

    # combine both teams
    combined_full = pd.concat(team_frames.values(), ignore_index=True)

    # ------------------------------------------------------
    #  Robust detection/normalization of the Position column
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
    #  Classify and compute scores
    # ------------------------------------------------------
    combined_full["pos"] = combined_full["Pos"].apply(position_calcul)

    def _apply_score(row):
        bucket = row["pos"]
        if bucket == "GK":
            return gk_score_calc(row)
        elif bucket == "FWD":
            return fwd_score_calc(row)
        elif bucket == "MID":
            return mid_score_calc(row)
        else:
            return def_score_calc(row)

    combined_full["score"] = combined_full.apply(_apply_score, axis=1)

    # Slim result for the UI
    result = combined_full[["Player", "Team", "pos", "score"]].copy()
    return result


# ----------------------------------------------------------
# DEBUGGING HELPER – score breakdown for one player (outfield)
# ----------------------------------------------------------

def debug_player_components(full_df: pd.DataFrame, player_name: str) -> dict:
    """
    Return a dict of the stats used in scoring for a given player (outfield),
    plus their position bucket and final score.
    """
    row = full_df[full_df["Player"] == player_name]
    if row.empty:
        raise ValueError(f"No player named '{player_name}' found.")
    row = row.iloc[0]

    pos_bucket = position_calcul(row.get("Pos", "MID"))

    if pos_bucket == "GK":
        # GK breakdown is simpler; return the inputs we use.
        data = {
            "Shot Stopping_GA": _get(row, "Shot Stopping_GA", 0),
            "Shot Stopping_Saves": _get(row, "Shot Stopping_Saves", 0),
            "Launched_Cmp": _get(row, "Launched_Cmp", 0),
            "Crosses_Stp": _get(row, "Crosses_Stp", 0),
            "Sweeper_#OPA": _get(row, "Sweeper_#OPA", 0),
        }
        data["pos_bucket"] = "GK"
        data["final_score"] = gk_score_calc(row)
        return data

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
    else:
        score = def_score_calc(row)

    data["pos_bucket"] = pos_bucket
    data["final_score"] = score
    return data
