import pandas as pd
from bs4 import BeautifulSoup
import sys
import io

# ------------------- BASIC HELPERS -------------------

def parse_minute(time_str):
    if pd.isna(time_str):
        return 0
    s = str(time_str)
    if '+' in s:
        base, extra = s.split('+', 1)
        return int(base) + int(extra)
    if ':' in s:
        base = s.split(':', 1)[0]
        return int(base)
    try:
        return int(s)
    except ValueError:
        return 0


def position_calcul(pos):
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


# ------------------- SCORING FUNCTIONS (ORIGINAL STYLE) -------------------

def def_score_calc(df, team_score, team_conc):
    score = (
        1.9 * df.get('Aerial Duels_Won', 0)
        - 1.5 * df.get('Aerial Duels_Lost', 0)
        + 2.7 * df.get('Performance_Tkl', 0)
        - 1.6 * df.get('Challenges_Lost', 0)
        + 2.7 * df.get('Performance_Int', 0)
        + 1.1 * df.get('Unnamed: 20_level_0_Clr', 0)
        + (10 - (5 * team_conc))
        + (3
           - 1.2 * df.get('Carries_Dis', 0)
           - 0.6 * (df.get('Performance_Fls', 0) + df.get('Performance_Off', 0))
           - 3.5 * df.get('Performance_OG', 0)
           - 5 * df.get('Unnamed: 21_level_0_Err', 0)
           )
        + df.get('Passes_Cmp', 0)/9
        - ((df.get('Passes_Att', 0) - df.get('Passes_Cmp', 0))/4.5)
        + df.get('Unnamed: 23_level_0_KP', 0)
        + df.get('Take-Ons_Succ', 0)*2.5
        - (df.get('Take-Ons_Att', 0) - df.get('Take-Ons_Succ', 0))*0.8
        + 1.1 * df.get('Blocks_Sh', 0)
        + 1.5 * df.get('Unnamed: 23_level_0_KP', 0)
        + 1.2 * df.get('Performance_Crs', 0)
        + 2.5 * df.get('Performance_SoT', 0)
        + (df.get('Performance_Sh', 0) - df.get('Performance_SoT', 0))/2
        + df.get('Unnamed: 5_level_0_Min', 0)/30
        + 10*df.get('Performance_Gls', 0)
        + 8*df.get('Performance_Ast', 0)
        - 5*df.get('Performance_CrdR', 0)
        - 5*df.get('Performance_PKcon', 0)
        - 5*(df.get('Performance_PKatt', 0) - df.get('Performance_PK', 0))
    )

    pk_won = df.get('Performance_PKwon', 0)
    pk_scored = df.get('Performance_PK', 0)

    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    minutes_played = df.get('Unnamed: 5_level_0_Min', 0)
    if (minutes_played <= 45) and (team_conc == 0):
        score -= 5

    return round(score, 0)


def mid_score_calc(df, team_score, team_conc):
    score = (
        1.7 * df.get('Aerial Duels_Won', 0)
        - 1.5 * df.get('Aerial Duels_Lost', 0)
        + 2.6 * df.get('Performance_Tkl', 0)
        - 1.2 * df.get('Challenges_Lost', 0)
        + 2.5 * df.get('Performance_Int', 0)
        + 1.1 * df.get('Unnamed: 20_level_0_Clr', 0)
        + (4 - (2 * team_conc) + (2 * team_score))
        + (3
           - 1.1 * df.get('Carries_Dis', 0)
           - 0.6 * (df.get('Performance_Fls', 0) + df.get('Performance_Off', 0))
           - 3.3 * df.get('Performance_OG', 0)
           - 5 * df.get('Unnamed: 21_level_0_Err', 0)
           )
        + df.get('Passes_Cmp', 0)/6.6
        - ((df.get('Passes_Att', 0) - df.get('Passes_Cmp', 0))/3.2)
        + df.get('Unnamed: 23_level_0_KP', 0)
        + df.get('Take-Ons_Succ', 0)*2.9
        - (df.get('Take-Ons_Att', 0) - df.get('Take-Ons_Succ', 0))*0.8
        + 1.1 * df.get('Blocks_Sh', 0)
        + 1.5 * df.get('Unnamed: 23_level_0_KP', 0)
        + 1.2 * df.get('Performance_Crs', 0)
        + 2.2 * df.get('Performance_SoT', 0)
        + (df.get('Performance_Sh', 0) - df.get('Performance_SoT', 0))/4
        + df.get('Unnamed: 5_level_0_Min', 0)/30
        + 10*df.get('Performance_Gls', 0)
        + 8*df.get('Performance_Ast', 0)
        - 5*df.get('Performance_CrdR', 0)
        - 5*df.get('Performance_PKcon', 0)
        - 5*(df.get('Performance_PKatt', 0) - df.get('Performance_PK', 0))
    )

    pk_won = df.get('Performance_PKwon', 0)
    pk_scored = df.get('Performance_PK', 0)

    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    return round(score, 0)


def fwd_score_calc(df, team_score, team_conc):
    score = (
        1.4 * df.get('Aerial Duels_Won', 0)
        - 0.4 * df.get('Aerial Duels_Lost', 0)
        + 2.6 * df.get('Performance_Tkl', 0)
        - 1.0 * df.get('Challenges_Lost', 0)
        + 2.7 * df.get('Performance_Int', 0)
        + 0.8 * df.get('Unnamed: 20_level_0_Clr', 0)
        + (3 * team_score)
        + (5
           - 0.9 * df.get('Carries_Dis', 0)
           - 0.5 * (df.get('Performance_Fls', 0) + df.get('Performance_Off', 0))
           - 3.0 * df.get('Performance_OG', 0)
           - 5 * df.get('Unnamed: 21_level_0_Err', 0)
           )
        + df.get('Passes_Cmp', 0)/6
        - ((df.get('Passes_Att', 0) - df.get('Passes_Cmp', 0))/8.0)
        + df.get('Unnamed: 23_level_0_KP', 0)
        + df.get('Take-Ons_Succ', 0)*3.0
        - (df.get('Take-Ons_Att', 0) - df.get('Take-Ons_Succ', 0))*1.0
        + 0.8 * df.get('Blocks_Sh', 0)
        + 1.5 * df.get('Unnamed: 23_level_0_KP', 0)
        + 1.2 * df.get('Performance_Crs', 0)
        + 3.0 * df.get('Performance_SoT', 0)
        + (df.get('Performance_Sh', 0) - df.get('Performance_SoT', 0))/3
        + df.get('Unnamed: 5_level_0_Min', 0)/30
        + 10*df.get('Performance_Gls', 0)
        + 8*df.get('Performance_Ast', 0)
        - 5*df.get('Performance_CrdR', 0)
        - 5*df.get('Performance_PKcon', 0)
        - 5*(df.get('Performance_PKatt', 0) - df.get('Performance_PK', 0))
    )

    pk_won = df.get('Performance_PKwon', 0)
    pk_scored = df.get('Performance_PK', 0)

    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    return round(score, 0)


# ------------------- EVENTS FROM HTML (NO REQUESTS) -------------------

def get_match_events_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    events_wrap_div = soup.find('div', id='events_wrap')

    if not events_wrap_div:
        # No events – just return empty list
        return []

    match_events = []
    event_divs = events_wrap_div.find_all('div', class_='event')

    for event_div in event_divs:
        time_div = event_div.find('div')
        time = time_div.get_text(strip=True).split("’")[0] if time_div else None

        event_type_div = event_div.find('div', class_='event_icon')
        if not event_type_div:
            continue

        event_classes = event_type_div.get('class', [])
        if 'goal' in event_classes or 'penalty_goal' in event_classes:
            event_kind = 'Goal'
        elif 'yellow_card' in event_classes:
            event_kind = 'Yellow Card'
        elif 'substitute_in' in event_classes:
            event_kind = 'Substitution'
        else:
            event_kind = 'Unknown Event'

        if event_kind == 'Substitution':
            player_on_tag = event_div.find('a')
            player_on = player_on_tag.get_text(strip=True) if player_on_tag else None

            player_info_div = event_type_div.find_next_sibling('div')
            small_tags = player_info_div.find_all('small') if player_info_div else []
            player_off = None
            for small_tag in small_tags:
                if 'for' in small_tag.get_text(strip=True):
                    player_off_tag = small_tag.find('a')
                    player_off = player_off_tag.get_text(strip=True) if player_off_tag else None
                    break

            match_events.append({
                'time': time,
                'event_kind': event_kind,
                'player_on': player_on,
                'player_off': player_off,
            })
        else:
            player_tag = event_div.find('a')
            player = player_tag.get_text(strip=True) if player_tag else None

            scoreline_tag = event_div.find('small')
            scoreline = scoreline_tag.get_text(strip=True) if scoreline_tag else None

            match_events.append({
                'time': time,
                'event_kind': event_kind,
                'player': player,
                'scoreline': scoreline
            })

    return match_events


def process_match_events(match_events, df_home, df_away):
    import pandas as pd

    team_home_players = set(df_home['Unnamed: 0_level_0_Player'].astype(str).str.strip())
    team_away_players = set(df_away['Unnamed: 0_level_0_Player'].astype(str).str.strip())

    def get_team(player_name):
        if player_name in team_home_players:
            return 'Home'
        elif player_name in team_away_players:
            return 'Away'
        else:
            return 'Unknown'

    scoreline_timeline = [{'minute': 0, 'home_goals': 0, 'away_goals': 0}]
    current_home_goals = 0
    current_away_goals = 0

    for event in match_events:
        if event['event_kind'] == 'Goal' and event.get('player'):
            minute = parse_minute(event['time'])
            scorer = event['player']
            scoring_team = get_team(scorer)

            if scoring_team == 'Home':
                current_home_goals += 1
            elif scoring_team == 'Away':
                current_away_goals += 1

            scoreline_timeline.append({
                'minute': minute,
                'home_goals': current_home_goals,
                'away_goals': current_away_goals
            })

    match_end_time = 90
    if scoreline_timeline[-1]['minute'] < match_end_time:
        scoreline_timeline.append({
            'minute': match_end_time,
            'home_goals': current_home_goals,
            'away_goals': current_away_goals
        })

    def get_scoreline_before_minute(minute):
        for entry in reversed(scoreline_timeline):
            if entry['minute'] <= minute:
                return entry
        return {'home_goals': 0, 'away_goals': 0}

    players = {}
    for event in match_events:
        if event['event_kind'] != 'Substitution':
            continue
        minute = parse_minute(event['time'])
        player_on = event['player_on']
        player_off = event['player_off']

        if player_on:
            players[player_on] = {
                'team': get_team(player_on),
                'on_time': minute,
                'off_time': match_end_time
            }

        if player_off:
            if player_off in players:
                players[player_off]['off_time'] = minute
            else:
                players[player_off] = {
                    'team': get_team(player_off),
                    'on_time': 0,
                    'off_time': minute
                }

    all_players = set(team_home_players) | set(team_away_players)
    for player in all_players:
        if player not in players:
            players[player] = {
                'team': get_team(player),
                'on_time': 0,
                'off_time': match_end_time
            }

    player_stats = []
    final_scoreline = scoreline_timeline[-1]

    for player, data in players.items():
        team = data['team']
        on_time = data['on_time']
        off_time = data['off_time']
        minutes_played = off_time - on_time

        scoreline_before_on = get_scoreline_before_minute(on_time)
        scoreline_before_off = get_scoreline_before_minute(off_time)

        if on_time == 0 and off_time == match_end_time:
            goals_scored = final_scoreline['home_goals'] if team == 'Home' else final_scoreline['away_goals']
            goals_conceded = final_scoreline['away_goals'] if team == 'Home' else final_scoreline['home_goals']
        elif on_time == 0:
            goals_scored = scoreline_before_off['home_goals'] if team == 'Home' else scoreline_before_off['away_goals']
            goals_conceded = scoreline_before_off['away_goals'] if team == 'Home' else scoreline_before_off['home_goals']
        elif off_time == match_end_time:
            goals_scored = (
                final_scoreline['home_goals'] - scoreline_before_on['home_goals']
                if team == 'Home' else
                final_scoreline['away_goals'] - scoreline_before_on['away_goals']
            )
            goals_conceded = (
                final_scoreline['away_goals'] - scoreline_before_on['away_goals']
                if team == 'Home' else
                final_scoreline['home_goals'] - scoreline_before_on['home_goals']
            )
        else:
            goals_scored = (
                scoreline_before_off['home_goals'] - scoreline_before_on['home_goals']
                if team == 'Home' else
                scoreline_before_off['away_goals'] - scoreline_before_on['away_goals']
            )
            goals_conceded = (
                scoreline_before_off['away_goals'] - scoreline_before_on['away_goals']
                if team == 'Home' else
                scoreline_before_off['home_goals'] - scoreline_before_on['home_goals']
            )

        player_stats.append({
            'Unnamed: 0_level_0_Player': player,
            'minutes_played': minutes_played,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded
        })

    df_match_stats = pd.DataFrame(player_stats)
    df_home = df_home.merge(df_match_stats, on='Unnamed: 0_level_0_Player', how='left')
    df_away = df_away.merge(df_match_stats, on='Unnamed: 0_level_0_Player', how='left')

    df_home['minutes_played'] = df_home['minutes_played'].fillna(90)
    df_home['goals_scored'] = df_home['goals_scored'].fillna(0)
    df_home['goals_conceded'] = df_home['goals_conceded'].fillna(0)

    df_away['minutes_played'] = df_away['minutes_played'].fillna(90)
    df_away['goals_scored'] = df_away['goals_scored'].fillna(0)
    df_away['goals_conceded'] = df_away['goals_conceded'].fillna(0)

    return df_home, df_away


# ------------------- CORE: READ & MERGE TABLES (HARD-CODED INDICES) -------------------

def _flatten_columns(df):
    df.columns = ['_'.join([str(x) for x in col if str(x) != 'nan']).strip('_')
                  for col in df.columns.values]
    return df


def calc_all_players_from_html(html_content):
    """
    Main entry: takes the HTML as a string (from uploaded file),
    hard-codes FBref table indices like your old code, and returns
    a stacked DataFrame with [name, score, pos].
    """
    # 1) Read ALL tables with 2-row headers like FBref
    url = pd.read_html(io.StringIO(html_content), header=[0, 1])

    # 2) Define columns to keep (same as original)
    cols_to_keep_summary = [
        'Unnamed: 0_level_0_Player', 'Unnamed: 5_level_0_Min',
        'Performance_Gls', 'Performance_Ast', 'Performance_PK', 'Performance_PKatt',
        'Performance_Sh', 'Performance_SoT', 'Performance_CrdY', 'Performance_CrdR',
        'Performance_Tkl', 'Performance_Int', 'Passes_Cmp', 'Passes_Att',
        'Take-Ons_Att', 'Take-Ons_Succ'
    ]
    cols_to_keep_passing = ['Unnamed: 0_level_0_Player', 'Unnamed: 23_level_0_KP']
    cols_to_keep_def = [
        'Unnamed: 0_level_0_Player', 'Challenges_Lost',
        'Unnamed: 20_level_0_Clr', 'Unnamed: 21_level_0_Err', 'Blocks_Sh'
    ]
    cols_to_keep_poss = ['Unnamed: 0_level_0_Player', 'Carries_Dis']
    cols_to_keep_misc = [
        'Unnamed: 0_level_0_Player', 'Performance_Fls',
        'Performance_Off', 'Performance_Crs', 'Performance_OG',
        'Aerial Duels_Won', 'Aerial Duels_Lost', 'Performance_PKwon', 'Performance_PKcon'
    ]

    # --- HOME TEAM TABLES (hard-coded indices, like original) ---
    df_summary = _flatten_columns(url[3])
    df_summary = df_summary[[c for c in cols_to_keep_summary if c in df_summary.columns]]
    df_passing = _flatten_columns(url[4])
    df_passing = df_passing[[c for c in cols_to_keep_passing if c in df_passing.columns]]
    df_def = _flatten_columns(url[6])
    df_def = df_def[[c for c in cols_to_keep_def if c in df_def.columns]]
    df_poss = _flatten_columns(url[7])
    df_poss = df_poss[[c for c in cols_to_keep_poss if c in df_poss.columns]]
    df_misc = _flatten_columns(url[8])
    df_misc = df_misc[[c for c in cols_to_keep_misc if c in df_misc.columns]]

    df_home = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player', how='inner')
    df_home = df_home.merge(df_def, on='Unnamed: 0_level_0_Player', how='inner')
    df_home = df_home.merge(df_misc, on='Unnamed: 0_level_0_Player', how='inner')
    df_home = df_home.merge(df_poss, on='Unnamed: 0_level_0_Player', how='inner')

    # --- AWAY TEAM TABLES (hard-coded indices, like original) ---
    df_summary = _flatten_columns(url[10])
    df_summary = df_summary[[c for c in cols_to_keep_summary if c in df_summary.columns]]
    df_passing = _flatten_columns(url[11])
    df_passing = df_passing[[c for c in cols_to_keep_passing if c in df_passing.columns]]
    df_def = _flatten_columns(url[13])
    df_def = df_def[[c for c in cols_to_keep_def if c in df_def.columns]]
    df_poss = _flatten_columns(url[14])
    df_poss = df_poss[[c for c in cols_to_keep_poss if c in df_poss.columns]]
    df_misc = _flatten_columns(url[15])
    df_misc = df_misc[[c for c in cols_to_keep_misc if c in df_misc.columns]]

    df_away = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player', how='inner')
    df_away = df_away.merge(df_def, on='Unnamed: 0_level_0_Player', how='inner')
    df_away = df_away.merge(df_misc, on='Unnamed: 0_level_0_Player', how='inner')
    df_away = df_away.merge(df_poss, on='Unnamed: 0_level_0_Player', how='inner')

    # 3) Events & minutes-based goals scored/conceded
    events = get_match_events_from_html(html_content)
    df_home, df_away = process_match_events(events, df_home, df_away)

    # 4) Loop over players and compute scores, exactly like old code
    home_scores = []
    for i in range(0, url[3].shape[0] - 2):
        name = url[3].iloc[i, 0]
        pos_raw = url[3].iloc[i, 3]  # position column from summary table
        pos = position_calcul(pos_raw)

        row_df = df_home[df_home['Unnamed: 0_level_0_Player'] == name]
        if row_df.empty:
            continue
        row = row_df.iloc[0]

        team_score = row.get('goals_scored', 0)
        team_conc = row.get('goals_conceded', 0)

        if pos == "FWD":
            score = fwd_score_calc(row, team_score, team_conc)
        elif pos == "MID":
            score = mid_score_calc(row, team_score, team_conc)
        else:
            score = def_score_calc(row, team_score, team_conc)

        home_scores.append([name, score, pos])

    home_df = pd.DataFrame(home_scores, columns=["name", "score", "pos"])

    away_scores = []
    for i in range(0, url[10].shape[0] - 2):
        name = url[10].iloc[i, 0]
        pos_raw = url[10].iloc[i, 3]
        pos = position_calcul(pos_raw)

        row_df = df_away[df_away['Unnamed: 0_level_0_Player'] == name]
        if row_df.empty:
            continue
        row = row_df.iloc[0]

        team_score = row.get('goals_scored', 0)
        team_conc = row.get('goals_conceded', 0)

        if pos == "FWD":
            score = fwd_score_calc(row, team_score, team_conc)
        elif pos == "MID":
            score = mid_score_calc(row, team_score, team_conc)
        else:
            score = def_score_calc(row, team_score, team_conc)

        away_scores.append([name, score, pos])

    away_df = pd.DataFrame(away_scores, columns=["name", "score", "pos"])

    stacked_df = pd.concat([home_df, away_df], axis=0, ignore_index=True)

    # original hack
    stacked_df = stacked_df[stacked_df["name"] != "Pedrinho"]

    stacked_df['score'] = stacked_df['score'].astype(int)

    return stacked_df


# Optional: CLI usage for debugging locally
if __name__ == "__main__":
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
        with open(html_path, "r", encoding="utf-8") as f:
            html_text = f.read()
        output = "match_output.csv" if len(sys.argv) < 3 else sys.argv[2]
        df = calc_all_players_from_html(html_text)
        df.to_csv(output, index=False)
        print(f"✅ Saved results for {html_path} → {output}")
