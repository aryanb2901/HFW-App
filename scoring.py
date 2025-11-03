import pandas as pd
from bs4 import BeautifulSoup

# --- all your existing scoring formulas go here unchanged ---
# keep def_score_calc, mid_score_calc, fwd_score_calc, position_calcul, process_match_events exactly as before

def calc_all_players_from_html(html_content):
    """Read FBref match HTML content directly instead of a live URL."""

    # Parse the tables from the HTML string
    try:
        url = pd.read_html(html_content)
    except ValueError as e:
        raise ValueError(f"Failed to parse HTML: {e}")

    # Keep all your existing columns and merging logic
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

    # Home team tables
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

    df_home = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player')
    df_home = df_home.merge(df_def, on='Unnamed: 0_level_0_Player')
    df_home = df_home.merge(df_misc, on='Unnamed: 0_level_0_Player')
    df_home = df_home.merge(df_poss, on='Unnamed: 0_level_0_Player')

    # Away team tables
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

    df_away = df_summary.merge(df_passing, on='Unnamed: 0_level_0_Player')
    df_away = df_away.merge(df_def, on='Unnamed: 0_level_0_Player')
    df_away = df_away.merge(df_misc, on='Unnamed: 0_level_0_Player')
    df_away = df_away.merge(df_poss, on='Unnamed: 0_level_0_Player')

    # Combine home + away for scoring
    stacked_df = pd.concat([df_home, df_away], axis=0)
    stacked_df = stacked_df[stacked_df["Unnamed: 0_level_0_Player"]!="Pedrinho"]
    stacked_df['score'] = 0  # placeholder — your score calcs go below

    # Add your scoring calculations here as-is
    # For each player, determine pos, goals_scored, goals_conceded, etc.
    # Use your same logic for FWD/MID/DEF scoring.

    return stacked_df
