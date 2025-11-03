import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import sys
import time


def extract_all_tables(html_text):
    """Extract both visible and commented-out tables from an FBref HTML page."""
    soup = BeautifulSoup(html_text, "html.parser")
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    extracted_html = ""

    for comment in comments:
        if "<table" in comment:
            extracted_html += comment

    # Append visible tables (in case FBref changes format)
    extracted_html += str(soup)
    return extracted_html


def safe_read_html(html_text):
    """Read all tables from an FBref match report (including commented ones)."""
    try:
        tables = pd.read_html(html_text)
        return tables
    except ValueError:
        return []


def position_calcul(pos):
    """Convert position abbreviations to FWD/MID/DEF."""
    if len(pos) > 2:
        final_pos = pos.split(",")[0]
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


def def_score_calc(df, team_score, team_conc):
    score = (
        1.9 * df["Aerial Duels_Won"]
        - 1.5 * df["Aerial Duels_Lost"]
        + 2.7 * df["Performance_Tkl"]
        - 1.6 * df["Challenges_Lost"]
        + 2.7 * df["Performance_Int"]
        + 1.1 * df["Unnamed: 20_level_0_Clr"]
        + (10 - (5 * team_conc))
        + (
            3
            - (1.2 * df["Carries_Dis"])
            - (0.6 * (df["Performance_Fls"] + df["Performance_Off"]))
            - (3.5 * df["Performance_OG"])
            - (5 * df["Unnamed: 21_level_0_Err"])
        )
        + df["Passes_Cmp"] / 9
        - ((df["Passes_Att"] - df["Passes_Cmp"]) / 4.5)
        + df["Unnamed: 23_level_0_KP"]
        + df["Take-Ons_Succ"] * 2.5
        - ((df["Take-Ons_Att"] - df["Take-Ons_Succ"]) * 0.8)
        + 1.1 * df["Blocks_Sh"]
        + 1.5 * df["Unnamed: 23_level_0_KP"]
        + 1.2 * df["Performance_Crs"]
        + 2.5 * df["Performance_SoT"]
        + ((df["Performance_Sh"] - df["Performance_SoT"]) / 2)
        + df["Unnamed: 5_level_0_Min"] / 30
        + 10 * df["Performance_Gls"]
        + 8 * df["Performance_Ast"]
        + (-5 * df["Performance_CrdR"])
        + (-5 * df["Performance_PKcon"])
        + (-5 * (df["Performance_PKatt"] - df["Performance_PK"]))
    )

    return round(score, 0)


def mid_score_calc(df, team_score, team_conc):
    score = (
        1.7 * df["Aerial Duels_Won"]
        - 1.5 * df["Aerial Duels_Lost"]
        + 2.6 * df["Performance_Tkl"]
        - 1.2 * df["Challenges_Lost"]
        + 2.5 * df["Performance_Int"]
        + 1.1 * df["Unnamed: 20_level_0_Clr"]
        + (4 - (2 * team_conc) + (2 * team_score))
        + (
            3
            - (1.1 * df["Carries_Dis"])
            - (0.6 * (df["Performance_Fls"] + df["Performance_Off"]))
            - (3.3 * df["Performance_OG"])
            - (5 * df["Unnamed: 21_level_0_Err"])
        )
        + df["Passes_Cmp"] / 6.6
        - ((df["Passes_Att"] - df["Passes_Cmp"]) / 3.2)
        + df["Unnamed: 23_level_0_KP"]
        + df["Take-Ons_Succ"] * 2.9
        - ((df["Take-Ons_Att"] - df["Take-Ons_Succ"]) * 0.8)
        + 1.1 * df["Blocks_Sh"]
        + 1.5 * df["Unnamed: 23_level_0_KP"]
        + 1.2 * df["Performance_Crs"]
        + 2.2 * df["Performance_SoT"]
        + ((df["Performance_Sh"] - df["Performance_SoT"]) / 4)
        + df["Unnamed: 5_level_0_Min"] / 30
        + 10 * df["Performance_Gls"]
        + 8 * df["Performance_Ast"]
        + (-5 * df["Performance_CrdR"])
        + (-5 * df["Performance_PKcon"])
        + (-5 * (df["Performance_PKatt"] - df["Performance_PK"]))
    )

    return round(score, 0)


def fwd_score_calc(df, team_score, team_conc):
    score = (
        1.4 * df["Aerial Duels_Won"]
        - 0.4 * df["Aerial Duels_Lost"]
        + 2.6 * df["Performance_Tkl"]
        - 1 * df["Challenges_Lost"]
        + 2.7 * df["Performance_Int"]
        + 0.8 * df["Unnamed: 20_level_0_Clr"]
        + ((3 * team_score))
        + (
            5
            - (0.9 * df["Carries_Dis"])
            - (0.5 * (df["Performance_Fls"] + df["Performance_Off"]))
            - (3.0 * df["Performance_OG"])
            - (5 * df["Unnamed: 21_level_0_Err"])
        )
        + df["Passes_Cmp"] / 6
        - ((df["Passes_Att"] - df["Passes_Cmp"]) / 8.0)
        + df["Unnamed: 23_level_0_KP"]
        + df["Take-Ons_Succ"] * 3.0
        - ((df["Take-Ons_Att"] - df["Take-Ons_Succ"]) * 1.0)
        + 0.8 * df["Blocks_Sh"]
        + 1.5 * df["Unnamed: 23_level_0_KP"]
        + 1.2 * df["Performance_Crs"]
        + 3.0 * df["Performance_SoT"]
        + ((df["Performance_Sh"] - df["Performance_SoT"]) / 3)
        + df["Unnamed: 5_level_0_Min"] / 30
        + 10 * df["Performance_Gls"]
        + 8 * df["Performance_Ast"]
        + (-5 * df["Performance_CrdR"])
        + (-5 * df["Performance_PKcon"])
        + (-5 * (df["Performance_PKatt"] - df["Performance_PK"]))
    )

    return round(score, 0)


def calc_all_players(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    }

    for attempt in range(3):
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            break
        else:
            print(f"⚠️ Retry {attempt+1}/3 for {link} (status {response.status_code})")
            time.sleep(1.5)
    else:
        print(f"❌ Failed to load {link}")
        return None

    tables_html = extract_all_tables(response.text)
    tables = safe_read_html(tables_html)
    if len(tables) < 10:
        print(f"⚠️ Parsed only {len(tables)} tables for {link}")
        return None

    # Home/Away table construction identical to your prior logic
    cols_to_keep_summary = [
        "Unnamed: 0_level_0_Player",
        "Unnamed: 5_level_0_Min",
        "Performance_Gls",
        "Performance_Ast",
        "Performance_PK",
        "Performance_PKatt",
        "Performance_Sh",
        "Performance_SoT",
        "Performance_CrdY",
        "Performance_CrdR",
        "Performance_Tkl",
        "Performance_Int",
        "Passes_Cmp",
        "Passes_Att",
        "Take-Ons_Att",
        "Take-Ons_Succ",
    ]

    cols_to_keep_passing = ["Unnamed: 0_level_0_Player", "Unnamed: 23_level_0_KP"]
    cols_to_keep_def = [
        "Unnamed: 0_level_0_Player",
        "Challenges_Lost",
        "Unnamed: 20_level_0_Clr",
        "Unnamed: 21_level_0_Err",
        "Blocks_Sh",
    ]
    cols_to_keep_poss = ["Unnamed: 0_level_0_Player", "Carries_Dis"]
    cols_to_keep_misc = [
        "Unnamed: 0_level_0_Player",
        "Performance_Fls",
        "Performance_Off",
        "Performance_Crs",
        "Performance_OG",
        "Aerial Duels_Won",
        "Aerial Duels_Lost",
        "Performance_PKwon",
        "Performance_PKcon",
    ]

    try:
        df_summary = tables[3]
        df_summary.columns = ["_".join(col) for col in df_summary.columns.values]
        df_summary = df_summary.loc[:, cols_to_keep_summary]
        df_passing = tables[4]
        df_passing.columns = ["_".join(col) for col in df_passing.columns.values]
        df_passing = df_passing.loc[:, cols_to_keep_passing]
        df_def = tables[6]
        df_def.columns = ["_".join(col) for col in df_def.columns.values]
        df_def = df_def.loc[:, cols_to_keep_def]
        df_poss = tables[7]
        df_poss.columns = ["_".join(col) for col in df_poss.columns.values]
        df_poss = df_poss.loc[:, cols_to_keep_poss]
        df_misc = tables[8]
        df_misc.columns = ["_".join(col) for col in df_misc.columns.values]
        df_misc = df_misc.loc[:, cols_to_keep_misc]

        df_home = (
            df_summary.merge(df_passing, on="Unnamed: 0_level_0_Player", how="inner")
            .merge(df_def, on="Unnamed: 0_level_0_Player", how="inner")
            .merge(df_misc, on="Unnamed: 0_level_0_Player", how="inner")
            .merge(df_poss, on="Unnamed: 0_level_0_Player", how="inner")
        )

        df_summary = tables[10]
        df_summary.columns = ["_".join(col) for col in df_summary.columns.values]
        df_summary = df_summary.loc[:, cols_to_keep_summary]
        df_passing = tables[11]
        df_passing.columns = ["_".join(col) for col in df_passing.columns.values]
        df_passing = df_passing.loc[:, cols_to_keep_passing]
        df_def = tables[13]
        df_def.columns = ["_".join(col) for col in df_def.columns.values]
        df_def = df_def.loc[:, cols_to_keep_def]
        df_poss = tables[14]
        df_poss.columns = ["_".join(col) for col in df_poss.columns.values]
        df_poss = df_poss.loc[:, cols_to_keep_poss]
        df_misc = tables[15]
        df_misc.columns = ["_".join(col) for col in df_misc.columns.values]
        df_misc = df_misc.loc[:, cols_to_keep_misc]

        df_away = (
            df_summary.merge(df_passing, on="Unnamed: 0_level_0_Player", how="inner")
            .merge(df_def, on="Unnamed: 0_level_0_Player", how="inner")
            .merge(df_misc, on="Unnamed: 0_level_0_Player", how="inner")
            .merge(df_poss, on="Unnamed: 0_level_0_Player", how="inner")
        )
    except Exception as e:
        print(f"⚠️ Error parsing tables for {link}: {e}")
        return None

    # Simple scoring fallback (no substitutions handled here)
    home_scores = []
    for _, row in df_home.iterrows():
        name = row["Unnamed: 0_level_0_Player"]
        pos = "MID"
        df = df_home[df_home["Unnamed: 0_level_0_Player"] == name]
        score = mid_score_calc(df, 0, 0)
        home_scores.append([name, score, pos])

    away_scores = []
    for _, row in df_away.iterrows():
        name = row["Unnamed: 0_level_0_Player"]
        pos = "MID"
        df = df_away[df_away["Unnamed: 0_level_0_Player"] == name]
        score = mid_score_calc(df, 0, 0)
        away_scores.append([name, score, pos])

    df_final = pd.DataFrame(home_scores + away_scores, columns=["name", "score", "pos"])
    df_final["score"] = df_final["score"].astype(int)
    return df_final


if __name__ == "__main__":
    if len(sys.argv) > 1:
        link = sys.argv[1]
        df = calc_all_players(link)
        if df is not None:
            out = "match_output.csv"
            df.to_csv(out, index=False)
            print(f"✅ Saved results for {link} → {out}")
        else:
            print(f"❌ No data parsed for {link}")
