import streamlit as st
import pandas as pd
from scoring import calc_all_players_from_html

st.set_page_config(page_title="HFW Soccer Scoring App (HTML Upload)", layout="wide")

st.title("⚽ HFW Soccer Scoring App (Upload Match HTML)")

uploaded_html = st.file_uploader("Upload FBref Match HTML file", type=["html"])

if uploaded_html is not None:
    try:
        html_content = uploaded_html.read().decode("utf-8")
        results_df = calc_all_players_from_html(html_content)

        if not results_df.empty:
            st.success("Scores calculated successfully ✅")

            st.dataframe(
                results_df.sort_values("score", ascending=False).reset_index(drop=True),
                use_container_width=True
            )

            top5 = results_df.sort_values("score", ascending=False).head(5)
            st.subheader("Top 5 Performers")
            st.table(top5)

            csv = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full Scores as CSV",
                data=csv,
                file_name="fantasy_scores.csv",
                mime="text/csv",
            )
        else:
            st.warning("No player data found in this file. Please ensure it's a full FBref match report.")

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a single FBref match HTML file to begin.")
