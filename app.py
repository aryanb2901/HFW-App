import streamlit as st
import pandas as pd
from scoring import calc_all_players_from_html  # uses your existing logic

st.set_page_config(page_title="Fantasy Soccer Scoring", layout="wide")

st.title("⚽ HFW Soccer Scoring App – Multiple Matches")

st.markdown(
    """
Upload one or more **FBref match report HTML files** (File → Save Page As… in your browser).  
We'll calculate scores for every match and give you **one combined CSV** of all players.
"""
)

# Multi-file uploader: user can pick 1 to N HTML files
uploaded_files = st.file_uploader(
    "Upload FBref match HTML files",
    type=["html", "htm"],
    accept_multiple_files=True,
)

if st.button("Calculate Scores"):
    if not uploaded_files:
        st.warning("Please upload at least one HTML file.")
    else:
        all_results = []
        for i, f in enumerate(uploaded_files, start=1):
            try:
                st.write(f"📄 Processing file {i}: **{f.name}**")
                # Read file content and decode to text
                html_bytes = f.read()
                html_text = html_bytes.decode("utf-8", errors="ignore")

                # Use your existing parser/scorer
                df_match = calc_all_players_from_html(html_text)

                # Tag with match/source name so you know which game it was
                df_match["Match"] = f.name

                all_results.append(df_match)

            except Exception as e:
                st.error(f"❌ Error processing {f.name}: {e}")

        if not all_results:
            st.error("No valid match data found to combine.")
        else:
            combined = pd.concat(all_results, ignore_index=True)

            st.success(f"✅ Calculated scores for {len(all_results)} match(es).")

            # Nice sorted view: by match, then score descending
            combined_display = combined.sort_values(
                ["Match", "score"],
                ascending=[True, False],
            ).reset_index(drop=True)

            st.subheader("Combined Player Scores")
            st.dataframe(combined_display, use_container_width=True)

            # Download combined CSV
            csv = combined_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Combined Scores as CSV",
                data=csv,
                file_name="fantasy_scores_combined.csv",
                mime="text/csv",
            )
