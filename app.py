import streamlit as st
from scoring import calc_all_players_from_html

st.title("⚽ HFW Soccer Scoring – HTML Auto Table Detection")
uploaded_html = st.file_uploader("Upload FBref match HTML", type=["html"])

if uploaded_html:
    html = uploaded_html.read().decode("utf-8")
    try:
        df = calc_all_players_from_html(html)
        st.success("✅ Tables detected and scores calculated")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Upload a saved FBref match HTML file to begin.")
