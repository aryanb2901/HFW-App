import pandas as pd
import io
from bs4 import BeautifulSoup

# ---------------------------------------------
# Helper: Detect correct "Summary" tables dynamically
# ---------------------------------------------
def find_summary_tables_from_html(html_text):
    """Return (home_df, away_df) as parsed tables from HTML."""
    soup = BeautifulSoup(html_text, "html.parser")
    tables = pd.read_html(io.StringIO(html_text))
    print(f"🔍 Found {len(tables)} tables total")

    # Identify table titles
    captions = [cap.get_text(strip=True) for cap in soup.find_all("caption")]
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])]

    # Find all tables that have a "Player" column
    candidates = []
    for i, t in enumerate(tables):
        cols = [str(c).strip() for c in t.columns.get_level_values(0)]
        if any("Player" in str(c) for c in cols) and "Min" in " ".join(cols):
            candidates.append((i, cols))

    print(f"✅ Candidate tables with 'Player' column: {[i for i, _ in candidates]}")

    # Usually, first two are home/away summary tables
    if len(candidates) < 2:
        raise ValueError("Could not find two valid team summary tables.")
    
    home_df = tables[candidates[0][0]]
    away_df = tables[candidates[1][0]]

    # Flatten multi-index headers
    home_df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in home_df.columns.values]
    away_df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in away_df.columns.values]

    print(f"🏠 Home table cols: {home_df.columns[:10]}")
    print(f"🛫 Away table cols: {away_df.columns[:10]}")
    return home_df, away_df

# ---------------------------------------------
# Position helper (same as before)
# ---------------------------------------------
def position_calcul(pos):
    if pd.isna(pos):
        return "MID"
    pos = str(pos).strip().split(",")[0]
    if pos.endswith("W"): return "FWD"
    elif pos.endswith("M"): return "MID"
    elif pos.endswith("B"): return "DEF"
    else: return "MID"

# ---------------------------------------------
# Scoring formulas (you can paste your old DEF/MID/FWD functions here)
# ---------------------------------------------
def def_score_calc(df, team_score, team_conc):
    return round(5 + team_score - team_conc, 1)  # temporary simplified for testing

def mid_score_calc(df, team_score, team_conc):
    return round(6 + team_score - 0.5 * team_conc, 1)

def fwd_score_calc(df, team_score, team_conc):
    return round(7 + 2 * team_score - team_conc, 1)

# ---------------------------------------------
# Main function for Streamlit
# ---------------------------------------------
def calc_all_players_from_html(html_text):
    home_df, away_df = find_summary_tables_from_html(html_text)
    all_players = []

    for team_df, team_label in [(home_df, "Home"), (away_df, "Away")]:
        for _, row in team_df.iterrows():
            name = row.get("Player") or row.get("Unnamed: 0_level_0_Player")
            pos = position_calcul(row.get("Pos"))
            goals = int(row.get("Gls", 0))
            conc = 0  # placeholder; can be refined later
            if pos == "DEF": score = def_score_calc(team_df.iloc[0:1], goals, conc)
            elif pos == "MID": score = mid_score_calc(team_df.iloc[0:1], goals, conc)
            else: score = fwd_score_calc(team_df.iloc[0:1], goals, conc)
            all_players.append({"name": name, "pos": pos, "team": team_label, "score": score})

    return pd.DataFrame(all_players)
