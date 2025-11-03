import streamlit as st
import pandas as pd
from scoring import calc_all_players  

st.set_page_config(page_title="Fantasy Soccer Scoring", layout="wide")
st.title("⚽ HFW Soccer Scoring App (Multi-Link Version)")

st.markdown("""
Paste multiple **FBref match links** (one per line) below.
The app will calculate scores for each match, then combine them all into one CSV for download.
""")

# Multi-link input box
links_input = st.text_area("Enter one FBref match link per line:")

if st.button("Calculate Combined Scores"):
    links = [l.strip() for l in links_input.splitlines() if l.strip()]
    if not links:
        st.warning("Please enter at least one valid FBref link.")
    else:
        all_results = []
        st.info(f"Processing {len(links)} links...")

        for i, link in enumerate(links, start=1):
            try:
                st.write(f"⚙️ Processing match {i}/{len(links)}:")
                results_df = calc_all_players(link)
                results_df["Match Link"] = link  # track which match each player is from
                all_results.append(results_df)
                st.success(f"✅ Done for match {i}")
            except Exception as e:
                st.error(f"❌ Error processing {link}: {e}")

        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            combined_df = combined_df.sort_values("score", ascending=False).reset_index(drop=True)

            st.success("🎉 Combined scores calculated successfully!")
            st.dataframe(combined_df, use_container_width=True)

            # Download combined CSV
            csv = combined_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Combined Matchweek CSV",
                data=csv,
                file_name="Combined_Matchweek.csv",
                mime="text/csv",
            )
