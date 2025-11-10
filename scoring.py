import pandas as pd
from bs4 import BeautifulSoup, Comment
import io
import sys

# -----------------------------
# Helpers
# -----------------------------

def parse_minute(time_str):
    if '+' in time_str:
        base, extra = time_str.split('+')
        return int(base) + int(extra)
    return int(time_str)


# -----------------------------
# Scoring functions (unchanged formulas)
# -----------------------------

def def_score_calc(df, team_score, team_conc):
    score = (
        1.9 * df['Aerial Duels_Won']
        - 1.5 * df['Aerial Duels_Lost']
        + 2.7 * df['Performance_Tkl']
        - 1.6 * df['Challenges_Lost']
        + 2.7 * df['Performance_Int']
        + 1.1 * df['Unnamed: 20_level_0_Clr']
        + (10 - (5 * team_conc))
        + (
            3
            - (1.2 * df['Carries_Dis'])
            - (0.6 * (df['Performance_Fls'] + df['Performance_Off']))
            - (3.5 * df['Performance_OG'])
            - (5 * df['Unnamed: 21_level_0_Err'])
        )
        + df['Passes_Cmp'] / 9
        - ((df['Passes_Att'] - df['Passes_Cmp']) / 4.5)
        + df['Unnamed: 23_level_0_KP']
        + df['Take-Ons_Succ'] * 2.5
        - ((df['Take-Ons_Att'] - df['Take-Ons_Succ']) * 0.8)
        + 1.1 * df['Blocks_Sh']
        + 1.5 * df['Unnamed: 23_level_0_KP']
        + 1.2 * df['Performance_Crs']
        + 2.5 * df['Performance_SoT']
        + ((df['Performance_Sh'] - df['Performance_SoT']) / 2)
        + df['Unnamed: 5_level_0_Min'] / 30
        + 10 * df['Performance_Gls']
        + 8 * df['Performance_Ast']
        + (-5 * df['Performance_CrdR'])
        + (-5 * df['Performance_PKcon'])
        + (-5 * (df['Performance_PKatt'] - df['Performance_PK']))
    )

    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]

    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    minutes_played = df['Unnamed: 5_level_0_Min'].values[0]

    if (minutes_played <= 45) and (team_conc == 0):
        score -= 5

    return round(score, 0)


def mid_score_calc(df, team_score, team_conc):
    score = (
        1.7 * df['Aerial Duels_Won']
        - 1.5 * df['Aerial Duels_Lost']
        + 2.6 * df['Performance_Tkl']
        - 1.2 * df['Challenges_Lost']
        + 2.5 * df['Performance_Int']
        + 1.1 * df['Unnamed: 20_level_0_Clr']
        + (4 - (2 * team_conc) + (2 * team_score))
        + (
            3
            - (1.1 * df['Carries_Dis'])
            - (0.6 * (df['Performance_Fls'] + df['Performance_Off']))
            - (3.3 * df['Performance_OG'])
            - (5 * df['Unnamed: 21_level_0_Err'])
        )
        + df['Passes_Cmp'] / 6.6
        - ((df['Passes_Att'] - df['Passes_Cmp']) / 3.2)
        + df['Unnamed: 23_level_0_KP']
        + df['Take-Ons_Succ'] * 2.9
        - ((df['Take-Ons_Att'] - df['Take-Ons_Succ']) * 0.8)
        + 1.1 * df['Blocks_Sh']
        + 1.5 * df['Unnamed: 23_level_0_KP']
        + 1.2 * df['Performance_Crs']
        + 2.2 * df['Performance_SoT']
        + ((df['Performance_Sh'] - df['Performance_SoT']) / 4)
        + df['Unnamed: 5_level_0_Min'] / 30
        + 10 * df['Performance_Gls']
        + 8 * df['Performance_Ast']
        + (-5 * df['Performance_CrdR'])
        + (-5 * df['Performance_PKcon'])
        + (-5 * (df['Performance_PKatt'] - df['Performance_PK']))
    )

    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]

    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    return round(score, 0)


def fwd_score_calc(df, team_score, team_conc):
    score = (
        1.4 * df['Aerial Duels_Won']
        - 0.4 * df['Aerial Duels_Lost']
        + 2.6 * df['Performance_Tkl']
        - 1 * df['Challenges_Lost']
        + 2.7 * df['Performance_Int']
        + 0.8 * df['Unnamed: 20_level_0_Clr']
        + (3 * team_score)
        + (
            5
            - (0.9 * df['Carries_Dis'])
            - (0.5 * (df['Performance_Fls'] + df['Performance_Off']))
            - (3.0 * df['Performance_OG'])
            - (5 * df['Unnamed: 21_level_0_Err'])
        )
        + df['Passes_Cmp'] / 6
        - ((df['Passes_Att'] - df['Passes_Cmp']) / 8.0)
        + df['Unnamed: 23_level_0_KP']
        + df['Take-Ons_Succ'] * 3.0
        - ((df['Take-Ons_Att'] - df['Take-Ons_Succ']) * 1.0)
        + 0.8 * df['Blocks_Sh']
        + 1.5 * df['Unnamed: 23_level_0_KP']
        + 1.2 * df['Performance_Crs']
        + 3.0 * df['Performance_SoT']
        + ((df['Performance_Sh'] - df['Performance_SoT']) / 3)
        + df['Unnamed: 5_level_0_Min'] / 30
        + 10 * df['Performance_Gls']
        + 8 * df['Performance_Ast']
        + (-5 * df['Performance_CrdR'])
        + (-5 * df['Performance_PKcon'])
        + (-5 * (df['Performance_PKatt'] - df['Performance_PK']))
    )

    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]

    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    return round(score, 0)


# -----------------------------
# Event parsing – from HTML (no requests)
# -----------------------------

def get_match_events_from_html(html_text):
    """Parse match events directly from the uploaded HTML."""
    soup = BeautifulSoup(html_text, 'html.parser')

    events_wrap_div = soup.find('div', id='events_wrap')
    if not events_wrap_div:
        raise ValueError("Could not find 'events_wrap' div in HTML.")

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


def position_calcul(pos):
    """Robust position parsing – avoids float/NaN issues."""
    if not isinstance(pos, str):
        return "MID"
    pos = pos.strip()
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


def process_match_events(match_events, df_home, df_away):
    """Same as your previous function; unchanged logic."""
    import pandas as pd

    team_home_players = set(df_home['Unnamed: 0_level_0_Player'].str.strip())
    team_away_players = set(df_away['Unnamed: 0_level_0_Player'].str.strip())

    def get_team(player_name):
        if player_name in team_home_players:
            return 'Home'
        elif player_name in team_away_players:
            return 'Away'
        else:
            return 'Unknown'

    def parse_time(time_str):
        if '+' in time_str:
            base_minute = time_str.split('+')[0]
            return int(base_minute)
        elif ':' in time_str:
            base_minute = time_str.split(':')[0]
            return int(base_minute)
        else:
            return int(time_str)

    scoreline_timeline = [{'minute': 0, 'home_goals': 0, 'away_goals': 0}]
    current_home_goals = 0
    current_away_goals = 0

    for event in match_events:
        if event['event_kind'] == 'Goal':
            minute = parse_time(event['time'])
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
        event_kind = event['event_kind']
        minute = parse_time(event['time'])

        if event_kind == 'Substitution':
            player_on = event['player_on']
            player_off = event['player_off']

            players[player_on] = {
                'team': get_team(player_on),
                'on_time': minute,
                'off_time': match_end_time
            }

            if player_off in players:
                players[player_off]['off_time'] = minute
            else:
                players[player_off] = {
                    'team': get_team(player_off),
                    'on_time': 0,
                    'off_time': minute
                }

    all_players = set(
        df_home['Unnamed: 0_level_0_Player'].tolist()
        + df_away['Unnamed: 0_level_0_Player'].tolist()
    )
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
                if team == 'Home'
                else final_scoreline['away_goals'] - scoreline_before_on['away_goals']
            )
            goals_conceded = (
                final_scoreline['away_goals'] - scoreline_before_on['away_goals']
                if team == 'Home'
                else final_scoreline['home_goals'] - scoreline_before_on['home_goals']
            )
        else:
            goals_scored = (
                scoreline_before_off['home_goals'] - scoreline_before_on['home_goals']
                if team == 'Home'
                else scoreline_before_off['away_goals'] - scoreline_before_on['away_goals']
            )
            goals_conceded = (
                scoreline_before_off['away_goals'] - scoreline_before_on['away_goals']
                if team == 'Home'
                else scoreline_before_off['home_goals'] - scoreline_before_on['home_goals']
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

    final_df = pd.concat([df_home, df_away], ignore_index=True)
    final_df['minutes_played'] = final_df['minutes_played'].fillna(90)
    final_df['goals_scored'] = final_df['goals_scored'].fillna(0)
    final_df['goals_conceded'] = final_df['goals_conceded'].fillna(0)

    return final_df


# -----------------------------
# MAIN: calculate scores from HTML (NOT from URL)
# -----------------------------

def calc_all_players_from_html(html_text: str) -> pd.DataFrame:
    """
    Main entry for Streamlit.
    Takes raw HTML (as string) of one FBref match report
    and returns a DataFrame with [name, score, pos].
    """

    # Parse *all* tables from HTML – exactly like old `pd.read_html(link)`
    url = pd.read_html(io.StringIO(html_text))

    # --- these blocks are copied from your original code, just using `url[...]` ---

    cols_to_keep_summary = [
        'Unnamed: 0_level_0_Player', 'Unnamed: 5_level_0_Min', 'Performance_Gls',
        'Performance_Ast', 'Performance_PK', 'Performance_PKatt',
        'Performance_Sh', 'Performance_SoT', 'Performance_CrdY',
        'Performance_CrdR', 'Performance_Tkl', 'Performance_Int',
        'Passes_Cmp', 'Passes_Att', 'Take-Ons_Att', 'Take-Ons_Succ'
    ]

    cols_to_keep_passing = ['Unnamed: 0_level_0_Player', 'Unnamed: 23_level_0_KP']
    cols_to_keep_def = [
        'Unnamed: 0_level_0_Player', 'Challenges_Lost',
        'Unnamed: 20_level_0_Clr', 'Unnamed: 21_level_0_Err', 'Blocks_Sh'
    ]
    cols_to_keep_poss = ['Unnamed: 0_level_0_Player', 'Carries_Dis']
    cols_to_keep_misc = [
        'Unnamed: 0_level_0_Player', 'Performance_Fls', 'Performance_Off',
        'Performance_Crs', 'Performance_OG', 'Aerial Duels_Won',
        'Aerial Duels_Lost', 'Performance_PKwon', 'Performance_PKcon'
    ]

    # --- HOME ---

    df_summary = url[3]
    df_summary.columns = ['_'.join(col) for col in df_summary.columns.values]
    df_summary = df_summary.loc[:, cols_to_keep_summary]

    df_passing = url[4]
    df_passing.columns = ['_'.join(col) for col in df_passing.columns.values]
    df_passing = df_passing.loc[:, cols_to_keep_passing]

    df_def = url[6]
    df_def.columns = ['_'.join(col) for col in df_def.columns.values]
    df_def = df_def.loc[:, cols_to_keep_def]

    df_poss = url[7]
    df_poss.columns = ['_'.join(col) for col in df_poss.columns.values]
    df_poss = df_poss.loc[:, cols_to_keep_poss]

    df_misc = url[8]
    df_misc.columns = ['_'.join(col) for col in df_misc.columns.values]
    df_misc = df_misc.loc[:, cols_to_keep_misc]

    df_home = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player', how='inner')
    df_home = df_home.merge(df_def, on='Unnamed: 0_level_0_Player', how='inner')
    df_home = df_home.merge(df_misc, on='Unnamed: 0_level_0_Player', how='inner')
    df_home = df_home.merge(df_poss, on='Unnamed: 0_level_0_Player', how='inner')

    # --- AWAY ---

    df_summary = url[10]
    df_summary.columns = ['_'.join(col) for col in df_summary.columns.values]
    df_summary = df_summary.loc[:, cols_to_keep_summary]

    df_passing = url[11]
    df_passing.columns = ['_'.join(col) for col in df_passing.columns.values]
    df_passing = df_passing.loc[:, cols_to_keep_passing]

    df_def = url[13]
    df_def.columns = ['_'.join(col) for col in df_def.columns.values]
    df_def = df_def.loc[:, cols_to_keep_def]

    df_poss = url[14]
    df_poss.columns = ['_'.join(col) for col in df_poss.columns.values]
    df_poss = df_poss.loc[:, cols_to_keep_poss]

    df_misc = url[15]
    df_misc.columns = ['_'.join(col) for col in df_misc.columns.values]
    df_misc = df_misc.loc[:, cols_to_keep_misc]

    df_away = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player', how='inner')
    df_away = df_away.merge(df_def, on='Unnamed: 0_level_0_Player', how='inner')
    df_away = df_away.merge(df_misc, on='Unnamed: 0_level_0_Player', how='inner')
    df_away = df_away.merge(df_poss, on='Unnamed: 0_level_0_Player', how='inner')

    # --- Events from HTML ---

    events = get_match_events_from_html(html_text)
    processed_events = process_match_events(events, df_home, df_away)

    # --- Loop players (same as your original) ---

    home_scores = []
    for i in range(0, url[3].shape[0] - 2):
        name = url[3].iloc[i, 0]
        pos = position_calcul(url[3].iloc[i, 3])
        df = df_home[df_home['Unnamed: 0_level_0_Player'] == name]
        team_score = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_scored'].iloc[0]
        team_conc = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_conceded'].iloc[0]
        if pos == "FWD":
            score = fwd_score_calc(df, team_score, team_conc)
        elif pos == "MID":
            score = mid_score_calc(df, team_score, team_conc)
        elif pos == "DEF":
            score = def_score_calc(df, team_score, team_conc)
        else:
            score = mid_score_calc(df, team_score, team_conc)
        home_scores.append([name, score, pos])

    home_df = pd.DataFrame(home_scores, columns=["name", "score", "pos"])

    away_scores = []
    for i in range(0, url[10].shape[0] - 2):
        name = url[10].iloc[i, 0]
        pos = position_calcul(url[10].iloc[i, 3])
        df = df_away[df_away['Unnamed: 0_level_0_Player'] == name]
        team_score = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_scored'].iloc[0]
        team_conc = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_conceded'].iloc[0]
        if pos == "FWD":
            score = fwd_score_calc(df, team_score, team_conc)
        elif pos == "MID":
            score = mid_score_calc(df, team_score, team_conc)
        elif pos == "DEF":
            score = def_score_calc(df, team_score, team_conc)
        else:
            score = mid_score_calc(df, team_score, team_conc)
        away_scores.append([name, score, pos])

    away_df = pd.DataFrame(away_scores, columns=["name", "score", "pos"])

    stacked_df = pd.concat([home_df, away_df], axis=0)
    stacked_df = stacked_df[stacked_df["name"] != "Pedrinho"]
    stacked_df['score'] = stacked_df['score'].astype(int)

    return stacked_df


# Optional CLI usage if you ever want it:
if __name__ == "__main__":
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
        with open(html_path, "r", encoding="utf-8") as f:
            html_text = f.read()
        output = "match_output.csv" if len(sys.argv) < 3 else sys.argv[2]
        df = calc_all_players_from_html(html_text)
        df.to_csv(output, index=False)
        print(f"✅ Saved results for {html_path} → {output}")
