import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import sys

# ----------------------------- scoring formulas -----------------------------
def def_score_calc(df, team_score, team_conc):
    score =(1.9*df['Aerial Duels_Won'] - 1.5*df['Aerial Duels_Lost'] + 2.7*df['Performance_Tkl']
            -1.6*df['Challenges_Lost'] + 2.7*df['Performance_Int'] + 1.1*df['Unnamed: 20_level_0_Clr']
            +(10-(5*team_conc))+(3-(1.2*df['Carries_Dis'])-(0.6*(df['Performance_Fls']+df['Performance_Off']))
            -(3.5*df['Performance_OG'])-(5*df['Unnamed: 21_level_0_Err']))
            + df['Passes_Cmp']/9 - ((df['Passes_Att']-df['Passes_Cmp'])/4.5) + df['Unnamed: 23_level_0_KP']
            + df['Take-Ons_Succ']*2.5 -((df['Take-Ons_Att']-df['Take-Ons_Succ'])*0.8)
            + 1.1*df['Blocks_Sh'] + 1.5*df['Unnamed: 23_level_0_KP'] + 1.2*df['Performance_Crs']
            + 2.5*df['Performance_SoT'] + ((df['Performance_Sh']-df['Performance_SoT'])/2)
            + df['Unnamed: 5_level_0_Min']/30 + 10*df['Performance_Gls'] + 8*df['Performance_Ast']
            + (-5*df['Performance_CrdR']) + (-5*df['Performance_PKcon'])
            + (-5*(df['Performance_PKatt']-df['Performance_PK'])))
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4
    
    minutes_played = df['Unnamed: 5_level_0_Min'].values[0]
    if (minutes_played <= 45) and (team_conc == 0):
        score -= 5
    
    return round(score,0)

def mid_score_calc(df, team_score, team_conc):
    score =(1.7*df['Aerial Duels_Won'] - 1.5*df['Aerial Duels_Lost'] + 2.6*df['Performance_Tkl']
            -1.2*df['Challenges_Lost'] + 2.5*df['Performance_Int'] + 1.1*df['Unnamed: 20_level_0_Clr']
            +(4-(2*team_conc)+(2*team_score))+(3-(1.1*df['Carries_Dis'])-(0.6*(df['Performance_Fls']+df['Performance_Off']))
            -(3.3*df['Performance_OG'])-(5*df['Unnamed: 21_level_0_Err']))
            + df['Passes_Cmp']/6.6 - ((df['Passes_Att']-df['Passes_Cmp'])/3.2) + df['Unnamed: 23_level_0_KP']
            + df['Take-Ons_Succ']*2.9 - ((df['Take-Ons_Att']-df['Take-Ons_Succ'])*0.8)
            + 1.1*df['Blocks_Sh'] + 1.5*df['Unnamed: 23_level_0_KP'] + 1.2*df['Performance_Crs']
            + 2.2*df['Performance_SoT'] + ((df['Performance_Sh']-df['Performance_SoT'])/4)
            + df['Unnamed: 5_level_0_Min']/30 + 10*df['Performance_Gls'] + 8*df['Performance_Ast']
            + (-5*df['Performance_CrdR']) + (-5*df['Performance_PKcon'])
            + (-5*(df['Performance_PKatt']-df['Performance_PK'])))
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4
    
    return round(score,0)

def fwd_score_calc(df, team_score, team_conc):
    score =(1.4*df['Aerial Duels_Won'] - 0.4*df['Aerial Duels_Lost'] + 2.6*df['Performance_Tkl']
            -1*df['Challenges_Lost'] + 2.7*df['Performance_Int'] + 0.8*df['Unnamed: 20_level_0_Clr']
            + ((3*team_score)) + (5-(0.9*df['Carries_Dis'])-(0.5*(df['Performance_Fls']+df['Performance_Off']))
            -(3.0*df['Performance_OG'])-(5*df['Unnamed: 21_level_0_Err']))
            + df['Passes_Cmp']/6 - ((df['Passes_Att']-df['Passes_Cmp'])/8.0) + df['Unnamed: 23_level_0_KP']
            + df['Take-Ons_Succ']*3.0 -((df['Take-Ons_Att']-df['Take-Ons_Succ'])*1.0)
            + 0.8*df['Blocks_Sh'] + 1.5*df['Unnamed: 23_level_0_KP'] + 1.2*df['Performance_Crs']
            + 3.0*df['Performance_SoT'] + ((df['Performance_Sh']-df['Performance_SoT'])/3)
            + df['Unnamed: 5_level_0_Min']/30 + 10*df['Performance_Gls'] + 8*df['Performance_Ast']
            + (-5*df['Performance_CrdR']) + (-5*df['Performance_PKcon'])
            + (-5*(df['Performance_PKatt']-df['Performance_PK'])))
    
    pk_won = df['Performance_PKwon'].values[0]
    pk_scored = df['Performance_PK'].values[0]
    if (pk_won == 1) and (pk_scored != 1):
        score += 6.4
    
    return round(score,0)

# ----------------------------- helper -----------------------------
def safe_flatten_cols(df):
    """Safely flatten columns whether multi-index or single-index"""
    df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df.columns.values]
    return df

# ----------------------------- main from HTML -----------------------------
def calc_all_players_from_html(html_content):
    """Read FBref match HTML content directly instead of fetching live."""
    url = pd.read_html(html_content)

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

    # HOME TEAM
    df_summary = safe_flatten_cols(url[3]).loc[:,cols_to_keep_summary]
    df_passing = safe_flatten_cols(url[4]).loc[:,cols_to_keep_passing]
    df_def = safe_flatten_cols(url[6]).loc[:,cols_to_keep_def]
    df_poss = safe_flatten_cols(url[7]).loc[:,cols_to_keep_poss]
    df_misc = safe_flatten_cols(url[8]).loc[:,cols_to_keep_misc]

    df_home = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player')
    df_home = df_home.merge(df_def, on='Unnamed: 0_level_0_Player')
    df_home = df_home.merge(df_misc, on='Unnamed: 0_level_0_Player')
    df_home = df_home.merge(df_poss, on='Unnamed: 0_level_0_Player')

    # AWAY TEAM
    df_summary = safe_flatten_cols(url[10]).loc[:,cols_to_keep_summary]
    df_passing = safe_flatten_cols(url[11]).loc[:,cols_to_keep_passing]
    df_def = safe_flatten_cols(url[13]).loc[:,cols_to_keep_def]
    df_poss = safe_flatten_cols(url[14]).loc[:,cols_to_keep_poss]
    df_misc = safe_flatten_cols(url[15]).loc[:,cols_to_keep_misc]

    df_away = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player')
    df_away = df_away.merge(df_def, on='Unnamed: 0_level_0_Player')
    df_away = df_away.merge(df_misc, on='Unnamed: 0_level_0_Player')
    df_away = df_away.merge(df_poss, on='Unnamed: 0_level_0_Player')

    # Combine
    stacked_df = pd.concat([df_home, df_away], axis=0)
    stacked_df = stacked_df[stacked_df["Unnamed: 0_level_0_Player"]!="Pedrinho"]
    stacked_df['score'] = 0  # placeholder to ensure column exists

    return stacked_df
