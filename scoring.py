import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import sys

def parse_minute(time_str):
    if '+' in time_str:
        base, extra = time_str.split('+')
        return int(base) + int(extra)
    return int(time_str)

def def_score_calc (df, team_score,team_conc):
    score =( 1.9*df['Aerial Duels_Won'] - 1.5*df[ 'Aerial Duels_Lost']+ 2.7*df['Performance_Tkl']
            -1.6*df['Challenges_Lost']+2.7*df['Performance_Int']+1.1*df['Unnamed: 20_level_0_Clr']
            +(10-(5*team_conc))+(3-(1.2*df['Carries_Dis'])-(0.6*(df['Performance_Fls']+df['Performance_Off']))
                               -(3.5*df['Performance_OG'])-(5*df[ 'Unnamed: 21_level_0_Err']))+
            df['Passes_Cmp']/9 - (( df['Passes_Att']-df['Passes_Cmp'])/4.5)+df['Unnamed: 23_level_0_KP']
            +df['Take-Ons_Succ']*2.5 -((df['Take-Ons_Att']-df['Take-Ons_Succ'])*0.8)+
            1.1*df[ 'Blocks_Sh']+1.5*df['Unnamed: 23_level_0_KP']+1.2*df['Performance_Crs']+
            2.5*df['Performance_SoT']+((df['Performance_Sh']-df['Performance_SoT'])/2)+
            df['Unnamed: 5_level_0_Min']/30 + 10*df['Performance_Gls']+8*df['Performance_Ast']+
            (-5*df['Performance_CrdR'])+(-5*df['Performance_PKcon']) +(-5*(df['Performance_PKatt']-df[ 'Performance_PK'])))
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4
    
    
    minutes_played = df['Unnamed: 5_level_0_Min'].values[0]

    if (minutes_played <= 45) and (team_conc == 0):
            score -= 5
    
    return round(score,0)

def mid_score_calc (df, team_score,team_conc):
    score =( 1.7*df['Aerial Duels_Won'] - 1.5*df[ 'Aerial Duels_Lost']+ 2.6*df['Performance_Tkl']
            -1.2*df['Challenges_Lost']+2.5*df['Performance_Int']+1.1*df['Unnamed: 20_level_0_Clr']
            +(4-(2*team_conc)+(2*team_score))+(3-(1.1*df['Carries_Dis'])-(0.6*(df['Performance_Fls']+df['Performance_Off']))
                               -(3.3*df['Performance_OG'])-(5*df[ 'Unnamed: 21_level_0_Err']))+
            df['Passes_Cmp']/6.6- (( df['Passes_Att']-df['Passes_Cmp'])/3.2)+df['Unnamed: 23_level_0_KP']
            +df['Take-Ons_Succ']*2.9 -((df['Take-Ons_Att']-df['Take-Ons_Succ'])*0.8)+
            1.1*df[ 'Blocks_Sh']+1.5*df['Unnamed: 23_level_0_KP']+1.2*df['Performance_Crs']+
            2.2*df['Performance_SoT']+((df['Performance_Sh']-df['Performance_SoT'])/4)+
            df['Unnamed: 5_level_0_Min']/30 + 10*df['Performance_Gls']+8*df['Performance_Ast']+
            (-5*df['Performance_CrdR'])+(-5*df['Performance_PKcon']) +(-5*(df['Performance_PKatt']-df[ 'Performance_PK'])))
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4
            
    return round(score,0)

def fwd_score_calc (df, team_score,team_conc):
    score =( 1.4*df['Aerial Duels_Won'] - 0.4*df[ 'Aerial Duels_Lost']+ 2.6*df['Performance_Tkl']
            -1*df['Challenges_Lost']+2.7*df['Performance_Int']+0.8*df['Unnamed: 20_level_0_Clr']
            +((3*team_score))+(5-(0.9*df['Carries_Dis'])-(0.5*(df['Performance_Fls']+df['Performance_Off']))
                               -(3.0*df['Performance_OG'])-(5*df[ 'Unnamed: 21_level_0_Err']))+
            df['Passes_Cmp']/6 - (( df['Passes_Att']-df['Passes_Cmp'])/8.0)+df['Unnamed: 23_level_0_KP']
            +df['Take-Ons_Succ']*3.0 -((df['Take-Ons_Att']-df['Take-Ons_Succ'])*1.0)+
           0.8*df[ 'Blocks_Sh']+1.5*df['Unnamed: 23_level_0_KP']+1.2*df['Performance_Crs']+
            3.0*df['Performance_SoT']+((df['Performance_Sh']-df['Performance_SoT'])/3)+
            df['Unnamed: 5_level_0_Min']/30 + 10*df['Performance_Gls']+8*df['Performance_Ast']+
            (-5*df['Performance_CrdR'])+(-5*df['Performance_PKcon'])+(-5*(df['Performance_PKatt']-df[ 'Performance_PK'])))
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4
    
    return round(score,0)

def calc_score (link, name, pos, team_score, team_conc):
    url = pd.read_html(link)
    cols_to_keep_summary = ['Unnamed: 0_level_0_Player','Unnamed: 5_level_0_Min', 'Performance_Gls',
    'Performance_Ast', 'Performance_PK', 'Performance_PKatt',
    'Performance_Sh', 'Performance_SoT', 'Performance_CrdY',
    'Performance_CrdR','Performance_Tkl',
    'Performance_Int','Passes_Cmp', 'Passes_Att', 
    'Take-Ons_Att', 'Take-Ons_Succ']

    cols_to_keep_passing = ['Unnamed: 0_level_0_Player','Unnamed: 23_level_0_KP']
    cols_to_keep_def = ['Unnamed: 0_level_0_Player','Challenges_Lost', 'Unnamed: 20_level_0_Clr',
                        'Unnamed: 21_level_0_Err', 'Blocks_Sh']
    cols_to_keep_poss = ['Unnamed: 0_level_0_Player', 'Carries_Dis']
    cols_to_keep_misc = ['Unnamed: 0_level_0_Player','Performance_Fls',
                         'Performance_Off','Performance_Crs','Performance_OG',
                         'Aerial Duels_Won', 'Aerial Duels_Lost', 'Performance_PKwon', 'Performance_PKcon']

    df_summary = url[3]
    df_summary.columns =  ['_'.join(col) for col in df_summary.columns.values]
    df_summary = df_summary.loc[:,cols_to_keep_summary]
    df_passing = url[4]
    df_passing.columns =  ['_'.join(col) for col in df_passing.columns.values]
    df_passing = df_passing.loc[:,cols_to_keep_passing]
    df_def = url[6]
    df_def.columns =  ['_'.join(col) for col in df_def.columns.values]
    df_def = df_def.loc[:,cols_to_keep_def]
    df_poss = url[7]
    df_poss.columns =  ['_'.join(col) for col in df_poss.columns.values]
    df_poss= df_poss.loc[:,cols_to_keep_poss]
    df_misc = url[8]
    df_misc.columns =  ['_'.join(col) for col in df_misc.columns.values]
    df_misc = df_misc.loc[:,cols_to_keep_misc]

    df_home = df_summary.merge(df_passing, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_home = df_home.merge(df_def, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_home = df_home.merge(df_misc, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_home = df_home.merge(df_poss,on= 'Unnamed: 0_level_0_Player', how = 'inner')
    
    df_summary = url[10]
    df_summary.columns =  ['_'.join(col) for col in df_summary.columns.values]
    df_summary = df_summary.loc[:,cols_to_keep_summary]
    df_passing = url[11]
    df_passing.columns =  ['_'.join(col) for col in df_passing.columns.values]
    df_passing = df_passing.loc[:,cols_to_keep_passing]
    df_def = url[13]
    df_def.columns =  ['_'.join(col) for col in df_def.columns.values]
    df_def = df_def.loc[:,cols_to_keep_def]
    df_poss = url[14]
    df_poss.columns =  ['_'.join(col) for col in df_poss.columns.values]
    df_poss= df_poss.loc[:,cols_to_keep_poss]
    df_misc = url[15]
    df_misc.columns =  ['_'.join(col) for col in df_misc.columns.values]
    df_misc = df_misc.loc[:,cols_to_keep_misc]

    df_away = df_summary.merge(df_passing, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_away = df_away.merge(df_def, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_away = df_away.merge(df_misc, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_away = df_away.merge(df_poss,on= 'Unnamed: 0_level_0_Player', how = 'inner')
    
    stacked_df = pd.concat([df_home,df_away],axis=0)
    stacked_df.reset_index(drop=True, inplace=True)
    
    df = stacked_df[stacked_df['Unnamed: 0_level_0_Player'] == name]
    
    team_score = team_score
    team_conc =  team_conc
    
    if pos == "FWD":
        score = fwd_score_calc(df, team_score, team_conc)
    elif pos =="MID":
        score = mid_score_calc(df, team_score, team_conc)
    elif pos =="DEF":
        score = def_score_calc(df, team_score, team_conc)
        
    return score


def get_match_events(link):
    # Fetch the page content
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Bot/0.1)"
    }
    response = requests.get(link, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch the page: Status code {response.status_code}")

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the div with id "events_wrap"
    events_wrap_div = soup.find('div', id='events_wrap')

    if not events_wrap_div:
        raise ValueError("Could not find 'events_wrap' div.")

    # Create a list to store events
    match_events = []

    # Iterate through each event div
    event_divs = events_wrap_div.find_all('div', class_='event')
    
    for event_div in event_divs:
        # Time of the event (e.g., 27', 33')
        time_div = event_div.find('div')
        time = time_div.get_text(strip=True).split("’")[0] if time_div else None

        # Find the event type (goal, card, substitution, etc.)
        event_type_div = event_div.find('div', class_='event_icon')
        if event_type_div:
            event_classes = event_type_div.get('class', [])
            if 'goal' in event_classes:
                event_kind = 'Goal'
            elif 'penalty_goal' in event_classes:
                event_kind = 'Goal'
            elif 'yellow_card' in event_classes:
                event_kind = 'Yellow Card'
            elif 'substitute_in' in event_classes:
                event_kind = 'Substitution'
            else:
                event_kind = 'Unknown Event'
        
            if event_kind == 'Substitution':
                # Extract player coming in (player_on)
                player_on_tag = event_div.find('a')
                player_on = player_on_tag.get_text(strip=True) if player_on_tag else None
                
                player_info_div = event_type_div.find_next_sibling('div')

                small_tags = player_info_div.find_all('small')
                player_off = None
                for small_tag in small_tags:
                    if 'for' in small_tag.get_text(strip=True):
                        player_off_tag = small_tag.find('a')
                        player_off = player_off_tag.get_text(strip=True) if player_off_tag else None
                        break  # Found the correct small tag

                # Append the substitution event to the match events list
                match_events.append({
                    'time': time,
                    'event_kind': event_kind,
                    'player_on': player_on,
                    'player_off': player_off,
                })
            else:
                # Get the player involved in the event
                player_tag = event_div.find('a')
                player = player_tag.get_text(strip=True) if player_tag else None
                
                # Get the scoreline after the event (if available)
                scoreline_tag = event_div.find('small')
                scoreline = scoreline_tag.get_text(strip=True) if scoreline_tag else None

                # Append the event to the match events list
                match_events.append({
                    'time': time,
                    'event_kind': event_kind,
                    'player': player,
                    'scoreline': scoreline
                })

    return match_events


def position_calcul(pos):
    if len(pos) > 2 :
        final_pos = pos.split(",")[0]
    else:
        final_pos = pos
    
    if final_pos.endswith("W"):
        return "FWD"
    elif final_pos.endswith ("M"):
        return "MID"
    elif final_pos.endswith ("B"):
        return "DEF"
    


def process_match_events(match_events, df_home, df_away):
    """
    Processes match events and returns a DataFrame with player statistics.

    Parameters:
    - match_events (list of dict): List of match events.
    - df_home (pd.DataFrame): DataFrame containing home team player data.
    - df_away (pd.DataFrame): DataFrame containing away team player data.

    Returns:
    - pd.DataFrame: DataFrame with player statistics including minutes played, goals scored, and goals conceded.
    """
    import pandas as pd

    # Combine home and away players into sets for team assignments
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

    # Build a scoreline timeline
    scoreline_timeline = [{'minute': 0, 'home_goals': 0, 'away_goals': 0}]
    current_home_goals = 0
    current_away_goals = 0

    # Collect goal events and sort them by time
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

    # Ensure the final scoreline is included
    match_end_time = 90  # Adjust if the match ended at a different time
    if scoreline_timeline[-1]['minute'] < match_end_time:
        scoreline_timeline.append({
            'minute': match_end_time,
            'home_goals': current_home_goals,
            'away_goals': current_away_goals
        })

    # Function to get scoreline just before a given minute
    def get_scoreline_before_minute(minute):
        for entry in reversed(scoreline_timeline):
            if entry['minute'] <= minute:
                return entry
        return {'home_goals': 0, 'away_goals': 0}

    # Build player intervals based on substitutions
    players = {}

    for event in match_events:
        event_kind = event['event_kind']
        minute = parse_time(event['time'])

        if event_kind == 'Substitution':
            player_on = event['player_on']
            player_off = event['player_off']

            # Player coming on
            players[player_on] = {
                'team': get_team(player_on),
                'on_time': minute,
                'off_time': match_end_time  # Until the end of the match
            }

            # Player going off
            if player_off in players:
                players[player_off]['off_time'] = minute
            else:
                players[player_off] = {
                    'team': get_team(player_off),
                    'on_time': 0,
                    'off_time': minute
                }

    # Add players who played full match
    all_players = set(df_home['Unnamed: 0_level_0_Player'].tolist() + df_away['Unnamed: 0_level_0_Player'].tolist())
    for player in all_players:
        if player not in players:
            players[player] = {
                'team': get_team(player),
                'on_time': 0,
                'off_time': match_end_time
            }

    # Calculate goals scored and conceded for each player
    player_stats = []
    final_scoreline = scoreline_timeline[-1]

    for player, data in players.items():
        team = data['team']
        on_time = data['on_time']
        off_time = data['off_time']
        minutes_played = off_time - on_time

        # Get scoreline before on_time and off_time
        scoreline_before_on = get_scoreline_before_minute(on_time)
        scoreline_before_off = get_scoreline_before_minute(off_time)

        if on_time == 0 and off_time == match_end_time:
            # Played full match
            goals_scored = final_scoreline['home_goals'] if team == 'Home' else final_scoreline['away_goals']
            goals_conceded = final_scoreline['away_goals'] if team == 'Home' else final_scoreline['home_goals']
        elif on_time == 0:
            # Subbed off
            goals_scored = scoreline_before_off['home_goals'] if team == 'Home' else scoreline_before_off['away_goals']
            goals_conceded = scoreline_before_off['away_goals'] if team == 'Home' else scoreline_before_off['home_goals']
        elif off_time == match_end_time:
            # Subbed on
            goals_scored = (final_scoreline['home_goals'] - scoreline_before_on['home_goals']) if team == 'Home' else (final_scoreline['away_goals'] - scoreline_before_on['away_goals'])
            goals_conceded = (final_scoreline['away_goals'] - scoreline_before_on['away_goals']) if team == 'Home' else (final_scoreline['home_goals'] - scoreline_before_on['home_goals'])
        else:
            # Subbed on and off (unlikely but handled)
            goals_scored = (scoreline_before_off['home_goals'] - scoreline_before_on['home_goals']) if team == 'Home' else (scoreline_before_off['away_goals'] - scoreline_before_on['away_goals'])
            goals_conceded = (scoreline_before_off['away_goals'] - scoreline_before_on['away_goals']) if team == 'Home' else (scoreline_before_off['home_goals'] - scoreline_before_on['home_goals'])

        player_stats.append({
            'Unnamed: 0_level_0_Player': player,
            'minutes_played': minutes_played,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded
        })

    # Create DataFrame with player statistics
    df_match_stats = pd.DataFrame(player_stats)

    # Merge with df_home and df_away
    df_home = df_home.merge(df_match_stats, on='Unnamed: 0_level_0_Player', how='left')
    df_away = df_away.merge(df_match_stats, on='Unnamed: 0_level_0_Player', how='left')

    # Combine home and away DataFrames
    final_df = pd.concat([df_home, df_away], ignore_index=True)

    # Fill NaN values in statistics with defaults
    final_df['minutes_played'] = final_df['minutes_played'].fillna(90)
    final_df['goals_scored'] = final_df['goals_scored'].fillna(0)
    final_df['goals_conceded'] = final_df['goals_conceded'].fillna(0)

    return final_df


def calc_all_players (link):

    # Define headers with a User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36'
    }

# Make the HTTP request with headers
    response = requests.get(link, headers=headers)

# Check if the request was successful
    if response.status_code == 200:
    # Use pd.read_html on the response content
        url = pd.read_html(response.text)
    # Now dfs is a list of DataFrames extracted from the page
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        
    cols_to_keep_summary = ['Unnamed: 0_level_0_Player','Unnamed: 5_level_0_Min', 'Performance_Gls',
    'Performance_Ast', 'Performance_PK', 'Performance_PKatt',
    'Performance_Sh', 'Performance_SoT', 'Performance_CrdY',
    'Performance_CrdR','Performance_Tkl',
    'Performance_Int','Passes_Cmp', 'Passes_Att', 
    'Take-Ons_Att', 'Take-Ons_Succ']

    cols_to_keep_passing = ['Unnamed: 0_level_0_Player','Unnamed: 23_level_0_KP']
    cols_to_keep_def = ['Unnamed: 0_level_0_Player','Challenges_Lost', 'Unnamed: 20_level_0_Clr',
                        'Unnamed: 21_level_0_Err', 'Blocks_Sh']
    cols_to_keep_poss = ['Unnamed: 0_level_0_Player', 'Carries_Dis']
    cols_to_keep_misc = ['Unnamed: 0_level_0_Player','Performance_Fls',
                         'Performance_Off','Performance_Crs','Performance_OG',
                         'Aerial Duels_Won', 'Aerial Duels_Lost', 'Performance_PKwon', 'Performance_PKcon']

    df_summary = url[3]
    df_summary.columns =  ['_'.join(col) for col in df_summary.columns.values]
    df_summary = df_summary.loc[:,cols_to_keep_summary]
    df_passing = url[4]
    df_passing.columns =  ['_'.join(col) for col in df_passing.columns.values]
    df_passing = df_passing.loc[:,cols_to_keep_passing]
    df_def = url[6]
    df_def.columns =  ['_'.join(col) for col in df_def.columns.values]
    df_def = df_def.loc[:,cols_to_keep_def]
    df_poss = url[7]
    df_poss.columns =  ['_'.join(col) for col in df_poss.columns.values]
    df_poss= df_poss.loc[:,cols_to_keep_poss]
    df_misc = url[8]
    df_misc.columns =  ['_'.join(col) for col in df_misc.columns.values]
    df_misc = df_misc.loc[:,cols_to_keep_misc]

    df_home = df_summary.merge(df_passing, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_home = df_home.merge(df_def, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_home = df_home.merge(df_misc, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_home = df_home.merge(df_poss,on= 'Unnamed: 0_level_0_Player', how = 'inner')
    
    df_summary = url[10]
    df_summary.columns =  ['_'.join(col) for col in df_summary.columns.values]
    df_summary = df_summary.loc[:,cols_to_keep_summary]
    df_passing = url[11]
    df_passing.columns =  ['_'.join(col) for col in df_passing.columns.values]
    df_passing = df_passing.loc[:,cols_to_keep_passing]
    df_def = url[13]
    df_def.columns =  ['_'.join(col) for col in df_def.columns.values]
    df_def = df_def.loc[:,cols_to_keep_def]
    df_poss = url[14]
    df_poss.columns =  ['_'.join(col) for col in df_poss.columns.values]
    df_poss= df_poss.loc[:,cols_to_keep_poss]
    df_misc = url[15]
    df_misc.columns =  ['_'.join(col) for col in df_misc.columns.values]
    df_misc = df_misc.loc[:,cols_to_keep_misc]

    df_away = df_summary.merge(df_passing, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_away = df_away.merge(df_def, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_away = df_away.merge(df_misc, on = 'Unnamed: 0_level_0_Player', how = 'inner')
    df_away = df_away.merge(df_poss,on= 'Unnamed: 0_level_0_Player', how = 'inner')
    
    events = get_match_events(link)
    processed_events = process_match_events(events, df_home, df_away)
    
    ## loop for home players
    
    home_scores = []
    for i in range(0,url[3].shape[0]-2):
        name = url[3].iloc[i,0]
        pos = position_calcul(url[3].iloc[i,3])
        df = df_home[df_home['Unnamed: 0_level_0_Player'] == name]
        team_score = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_scored'].iloc[0]
        team_conc = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_conceded'].iloc[0]
        if pos == "FWD":
            score = fwd_score_calc(df, team_score, team_conc)
        elif pos =="MID":
            score = mid_score_calc(df, team_score, team_conc)
        elif pos =="DEF":
            score = def_score_calc(df, team_score, team_conc)
        home_scores.append([name, score, pos])
    
    home_df = pd.DataFrame(home_scores, columns = ["name", "score", "pos"])
    
    away_scores = []
    for i in range(0,url[10].shape[0]-2):
        name = url[10].iloc[i,0]
        pos = position_calcul(url[10].iloc[i,3])
        df = df_away[df_away['Unnamed: 0_level_0_Player'] == name]
        team_score = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_scored'].iloc[0]
        team_conc = processed_events[processed_events['Unnamed: 0_level_0_Player'] == name]['goals_conceded'].iloc[0]
        if pos == "FWD":
            score = fwd_score_calc(df, team_score, team_conc)
        elif pos =="MID":
            score = mid_score_calc(df, team_score, team_conc)
        elif pos =="DEF":
            score = def_score_calc(df, team_score, team_conc)
        away_scores.append([name, score, pos])
    
    away_df = pd.DataFrame(away_scores, columns = ["name", "score", "pos"])

    
    
    stacked_df = pd.concat([home_df,away_df],axis=0)
    
    stacked_df = stacked_df[stacked_df["name"]!="Pedrinho"]
    
    stacked_df['score'] = stacked_df['score'].astype(int)
    
    
    return stacked_df
    
    if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        output = "match_output.csv" if len(sys.argv) < 3 else sys.argv[2]
        df = calculate_scores(url)  # existing function already in the file
        df.to_csv(output, index=False)
        print(f"✅ Saved results for {url} → {output}")
