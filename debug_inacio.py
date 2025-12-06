import pandas as pd
from scoring import calc_all_players_from_html, debug_player_components

# 1) Load the HTML you uploaded (adjust path if needed)
HTML_PATH = "Sporting CP vs. Club Brugge Match Report – Wednesday November 26, 2025 _ FBref.com.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_text = f.read()

# 2) Get the full scored dataframe for that match
full_scores_df = calc_all_players_from_html(html_text)

# 3) Show all Sporting players just to check it’s right
print("All players and scores:")
print(full_scores_df)

# 4) Debug just Gonçalo Inácio
player_name = "Gonçalo Inácio"  # must match the Player column spelling
debug = debug_player_components(full_scores_df.merge(
    # merge back all internal columns if you kept a slimmer df in calc_all_players_from_html
    full_scores_df, on=["Player", "Team", "pos", "score"], how="left"
), player_name)

print("\n--- Detailed breakdown for", player_name, "---")
for k, v in debug.items():
    print(f"{k}: {v}")
