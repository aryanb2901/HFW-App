import streamlit as st
import pandas as pd
from scoring import calc_all_players

st.set_page_config(page_title="⚽ Fantasy Soccer Scoring", layout="wide")

st.title("🏆 HFW Soccer Scoring App (Multi-Match Version)")

# --- Step 1: user chooses number of matches ---
num_matches = st.number_input(
    "How many matches are in this gameweek?", 
    min_value=1, 
    max_value=10, 
    value=1, 
    step=1
)

# --- Step 2: dynamically generate input boxes ---
match_links = []
for i in range(num_matches):
    link = st.text_input(f"Match {i+1} FBref link:", key=f"match_link_{i}")
    if link:
        match_links.append(link.strip())

# --- Step 3: Calculate scores when user clicks button ---
if st.button("⚙️ Calculate Scores"):
    if not match_links:
        st.warning("Please enter at least one valid FBref match link.")
    else:
        all_results = []
        for link in match_links:
            st.write(f"Processing: {link}")
            try:
                df = calc_all_players(link)
                if df is not None:
                    all_results.append(df)
                    st.success(f"✅ Processed {link}")
                else:
                    st.warning(f"⚠️ Skipped {link} (no valid data found)")
            except Exception as e:
                st.error(f"❌ Error processing {link}: {e}")

        if all_results:
            combined = pd.concat(all_results, ignore_index=True)
            combined = combined.sort_values("score", ascending=False).reset_index(drop=True)

            st.success("🎯 Combined scores generated successfully!")
            st.dataframe(combined, use_container_width=True)

            csv = combined.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Combined Scores (CSV)",
                data=csv,
                file_name="combined_gameweek_scores.csv",
                mime="text/csv",
            )
        else:
            st.warning("No valid match data found to combine.")
