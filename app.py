import streamlit as st
from model import get_top5_recommendations, get_all_full_titles
import difflib

# --- Page config ---
st.set_page_config(page_title="TokuRec", layout="wide")
st.title("The TokuRec Machine")

# --- Display function ---
def display_recommendations(recs):
    """Display top 5 recommendations in podium style with stats."""
    if len(recs) < 5:
        st.warning("Less than 5 recommendations available.")
    
    # Top center
    col1, col2, col3 = st.columns([2, 4, 2])
    with col2:
        rec = recs[0]
        st.markdown(f"<h2 style='text-align:center;'>{rec['Series']} {rec['Season']}</h2>", unsafe_allow_html=True)
        st.write(f"Score: {rec['Similarity']*100:.1f}%")
        st.write(f"Rating: {rec.get('Rating', 'N/A')}")
        st.write(f"Era: {rec.get('Era', 'N/A')}")
        st.markdown("---")
    
    # Middle left/right
    col_left, col_right = st.columns(2)
    with col_left:
        rec = recs[1]
        st.subheader(f"{rec['Series']} {rec['Season']}")
        st.write(f"Score: {rec['Similarity']*100:.1f}%")
        st.write(f"Rating: {rec.get('Rating', 'N/A')}")
        st.write(f"Era: {rec.get('Era', 'N/A')}")
    with col_right:
        rec = recs[2]
        st.subheader(f"{rec['Series']} {rec['Season']}")
        st.write(f"Score: {rec['Similarity']*100:.1f}%")
        st.write(f"Rating: {rec.get('Rating', 'N/A')}")
        st.write(f"Era: {rec.get('Era', 'N/A')}")
    
    # Bottom left/right
    col4, col5 = st.columns(2)
    with col4:
        rec = recs[3]
        st.subheader(f"{rec['Series']} {rec['Season']}")
        st.write(f"Score: {rec['Similarity']*100:.1f}%")
        st.write(f"Rating: {rec.get('Rating', 'N/A')}")
        st.write(f"Era: {rec.get('Era', 'N/A')}")
    with col5:
        rec = recs[4]
        st.subheader(f"{rec['Series']} {rec['Season']}")
        st.write(f"Score: {rec['Similarity']*100:.1f}%")
        st.write(f"Rating: {rec.get('Rating', 'N/A')}")
        st.write(f"Era: {rec.get('Era', 'N/A')}")

# --- Load all full titles from model ---
all_titles = get_all_full_titles()

# --- User input ---
user_input = st.text_input("What's your favorite Tokusatsu show?")

selected_title = None
if user_input:
    # Fuzzy match top 5 titles
    matches = difflib.get_close_matches(user_input, all_titles, n=5, cutoff=0.6)
    
    if matches:
        selected_title = st.selectbox("Did you mean one of these?", options=matches, index=0)
    else:
        st.write("No close matches found. Please check your spelling or enter a different title.")

# --- Recommendation button ---
if st.button("Henshin!"):
    if selected_title:
        try:
            recs = get_top5_recommendations(selected_title, n=5)
            st.write("Here are some recommendations for you:")
            display_recommendations(recs)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a Tokusatsu show title and select a match.")
