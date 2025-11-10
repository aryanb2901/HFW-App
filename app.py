import streamlit as st
import pandas as pd
from scoring import calc_all_players_from_html

st.set_page_config(page_title="Fantasy Soccer Scoring", layout="wide")
st.title("⚽ HFW Soccer Scoring App (HTML Upload)")

uploaded = st.file_uploader("Upload FBref match HTML", type=["html"])

if st.button("Calculate Scores") and uploaded:
    html_text = uploaded.read().decode("utf-8")
    try:
        results_df = calc_all_players_from_html(html_text)
        st.success("Scores calculated successfully ✅")
        st.dataframe(
            results_df.sort_values("score", ascending=False).reset_index(drop=True),
            use_container_width=True,
        )

        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Scores as CSV",
            data=csv,
            file_name="fantasy_scores.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Something went wrong: {e}")
