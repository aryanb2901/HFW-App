import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import sys

def parse_minute(time_str):
    if '+' in time_str:
        base, extra = time_str.split('+')
        return int(base) + int(extra)
    return int(time_str)

def def_score_calc(df, team_score, team_conc):
    score = (
        1.9*df['Aerial Duels_Won']
        - 1.5*df['Aerial Duels_Lost']
        + 2.7*df['Performance_Tkl']
        - 1.6*df['Challenges_Lost']
        + 2.7*df['Performance_Int']
        + 1.1*df['Unnamed: 20_level_0_Clr']
        + (10 - (5*team_conc))
        + (3 - (1.2*df['Carries_Dis']) - (0.6*(df['Performance_Fls'] + df['Performance_Off']))
           - (3.5*df['Performance_OG']) - (5*df['Unnamed: 21_level_0_Err']))
        + df['Passes_Cmp']/9
        - ((df['Passes_Att'] - df['Passes_Cmp']) / 4.5)
        + df['Unnamed: 23_level_0_KP']
        + df['Take-Ons_Succ']*2.5
        - ((df['Take-Ons_Att'] - df['Take-Ons_Succ']) * 0.8)
        + 1.1*df['Blocks_Sh']
        + 1.5*df['Unnamed: 23_level_0_KP']
        + 1.2*df['Performance_Crs']
        + 2.5*df['Performance_SoT']
        + ((df['Performance_Sh'] - df['Performance_SoT']) / 2)
        + df['Unnamed: 5_level_0_Min']/30
        + 10*df['Performance_Gls']
        + 8*df['Performance_Ast']
        + (-5*df['Performance_CrdR'])
        + (-5*df['Performance_PKcon'])
        + (-5*(df['Performance_PKatt'] - df['Performance_PK']))
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
        1.7*df['Aerial Duels_Won']
        - 1.5*df['Aerial Duels_Lost']
        + 2.6*df['Performance_Tkl']
        - 1.2*df['Challenges_Lost']
        + 2.5*df['Performance_Int']
        + 1.1*df['Unnamed: 20_level_0_Clr']
        + (4 - (2*team_conc) + (2*team_score))
        + (3 - (1.1*df['Carries_Dis']) - (0.6*(df['Performance_Fls'] + df['Performance_Off']))
           - (3.3*df['Performance_OG']) - (5*df['Unnamed: 21_level_0_Err']))
        + df['Passes_Cmp']/6.6
        - ((df['Passes_Att'] - df['Passes_Cmp']) / 3.2)
        + df['Unnamed: 23_level_0_KP']
        + df['Take-Ons_Succ']*2.9
        - ((df['Take-Ons_Att'] - df['Take-Ons_Succ']) * 0.8)
        + 1.1*df['Blocks_Sh']
        + 1.5*df['Unnamed: 23_level_0_KP']
        + 1.2*df['Performance_Crs']
        + 2.2*df['Performance_SoT']
        + ((df['Performance_Sh'] - df['Performance_SoT']) / 4)
        + df['Unnamed: 5_level_0_Min']/30
        + 10*df['Performance_Gls']
        + 8*df['Performance_Ast']
        + (-5*df['Performance_CrdR'])
        + (-5*df['Performance_PKcon'])
        + (-5*(df['Performance_PKatt'] - df['Performance_PK']))
    )
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    return round(score, 0)

def fwd_score_calc(df, team_score, team_conc):
    score = (
        1.4*df['Aerial Duels_Won']
        - 0.4*df['Aerial Duels_Lost']
        + 2.6*df['Performance_Tkl']
        - 1*df['Challenges_Lost']
        + 2.7*df['Performance_Int']
        + 0.8*df['Unnamed: 20_level_0_Clr']
        + ((3 * team_score))
        + (5 - (0.9*df['Carries_Dis']) - (0.5*(df['Performance_Fls'] + df['Performance_Off']))
           - (3.0*df['Performance_OG']) - (5*df['Unnamed: 21_level_0_Err']))
        + df['Passes_Cmp']/6
        - ((df['Passes_Att'] - df['Passes_Cmp']) / 8.0)
        + df['Unnamed: 23_level_0_KP']
        + df['Take-Ons_Succ']*3.0
        - ((df['Take-Ons_Att'] - df['Take-Ons_Succ']) * 1.0)
        + 0.8*df['Blocks_Sh']
        + 1.5*df['Unnamed: 23_level_0_KP']
        + 1.2*df['Performance_Crs']
        + 3.0*df['Performance_SoT']
        + ((df['Performance_Sh'] - df['Performance_SoT']) / 3)
        + df['Unnamed: 5_level_0_Min']/30
        + 10*df['Performance_Gls']
        + 8*df['Performance_Ast']
        + (-5*df['Performance_CrdR'])
        + (-5*df['Performance_PKcon'])
        + (-5*(df['Performance_PKatt'] - df['Performance_PK']))
    )

    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4

    return round(score, 0)

def calc_all_players(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(link, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to retrieve the page. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        html_tables = ""
        for c in comments:
            if "<table" in c:
                html_tables += c
        html_tables += str(soup)

        url = pd.read_html(html_tables)
        if not url or len(url) < 10:
            print(f"⚠️ Parsed only {len(url)} tables for {link}, expected more.")
            return None

    except Exception as e:
        print(f"❌ Exception fetching/parsing {link}: {e}")
        return None

    cols_to_keep_summary = ['Unnamed: 0_level_0_Player','Unnamed: 5_level_0_Min','Performance_Gls',
                            'Performance_Ast','Performance_PK','Performance_PKatt',
                            'Performance_Sh','Performance_SoT','Performance_CrdY',
                            'Performance_CrdR','Performance_Tkl','Performance_Int',
                            'Passes_Cmp','Passes_Att','Take-Ons_Att','Take-Ons_Succ']

    cols_to_keep_passing = ['Unnamed: 0_level_0_Player','Unnamed: 23_level_0_KP']
    cols_to_keep_def = ['Unnamed: 0_level_0_Player','Challenges_Lost','Unnamed: 20_level_0_Clr',
                        'Unnamed: 21_level_0_Err','Blocks_Sh']
    cols_to_keep_poss = ['Unnamed: 0_level_0_Player','Carries_Dis']
    cols_to_keep_misc = ['Unnamed: 0_level_0_Player','Performance_Fls','Performance_Off',
                         'Performance_Crs','Performance_OG','Aerial Duels_Won',
                         'Aerial Duels_Lost','Performance_PKwon','Performance_PKcon']

    # Home team
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

    # Away team
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

    events = get_match_events(link)
    processed_events = process_match_events(events, df_home, df_away)

    home_scores = []
    for i in range(0, url[3].shape[0]-2):
        name = url[3].iloc[i,0]
        pos = position_calcul(url[3].iloc[i,3])
        df = df_home[df_home['Unnamed: 0_level_0_Player'] == name]
        team_score = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_scored'].iloc[0]
        team_conc = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_conceded'].iloc[0]
        if pos == "FWD":
            score = fwd_score_calc(df, team_score, team_conc)
        elif pos == "MID":
            score = mid_score_calc(df, team_score, team_conc)
        else:
            score = def_score_calc(df, team_score, team_conc)
        home_scores.append([name, score, pos])

    home_df = pd.DataFrame(home_scores, columns=["name", "score", "pos"])

    away_scores = []
    for i in range(0, url[10].shape[0]-2):
        name = url[10].iloc[i,0]
        pos = position_calcul(url[10].iloc[i,3])
        df = df_away[df_away['Unnamed: 0_level_0_Player'] == name]
        team_score = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_scored'].iloc[0]
        team_conc = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_conceded'].iloc[0]
        if pos == "FWD":
            score = fwd_score_calc(df, team_score, team_conc)
        elif pos == "MID":
            score = mid_score_calc(df, team_score, team_conc)
        else:
            score = def_score_calc(df, team_score, team_conc)
        away_scores.append([name, score, pos])

    away_df = pd.DataFrame(away_scores, columns=["name", "score", "pos"])

    stacked_df = pd.concat([home_df, away_df], axis=0)
    stacked_df = stacked_df[stacked_df["name"] != "Pedrinho"]
    stacked_df['score'] = stacked_df['score'].astype(int)

    return stacked_df

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        output = "match_output.csv" if len(sys.argv) < 3 else sys.argv[2]
        df = calc_all_players(url)
        df.to_csv(output, index=False)
        print(f"✅ Saved results for {url} → {output}")
