import streamlit as st
import pandas as pd
from scoring import calc_all_players_from_html

st.set_page_config(page_title="HFW Soccer Scoring (HTML Upload)", layout="wide")
st.title("⚽ HFW Soccer Scoring App (HTML Upload Version)")

uploaded_html = st.file_uploader("Upload an FBref Match HTML file", type=["html"])

if uploaded_html:
    try:
        html_content = uploaded_html.read().decode("utf-8")
        results_df = calc_all_players_from_html(html_content)

        st.success("✅ Successfully parsed and scored players")
        st.dataframe(results_df.sort_values("score", ascending=False), use_container_width=True)

        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Combined Scores CSV",
            data=csv,
            file_name="fantasy_scores.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload an FBref match HTML file to start.")
