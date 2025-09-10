import streamlit as st
import difflib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Import from your model.py
from model import get_recommendations, build_feature_matrix

# =========================
# Streamlit page setup
# =========================
st.set_page_config(page_title="TokuRec", layout="wide")
st.title("The TokuRec Machine")

# =========================
# Load data
# =========================
df = pd.read_csv("tokusatsu_shows_enriched_cleaned.csv", encoding="utf-8-sig")

# Ensure full_title exists (matches model.py logic)
if "full_title" not in df.columns:
    df["Year"] = pd.to_datetime(df["First Air Date"], errors="coerce").dt.year
    df["full_title"] = df["Name"].fillna("") + " (" + df["Year"].fillna(0).astype(int).astype(str) + ")"

all_titles = df["full_title"].dropna().tolist()

# =========================
# Sidebar tuning (future use)
# =========================
st.sidebar.header("Recommendation Tuning")
pop_weight = st.sidebar.slider("Popularity Weight", 0.0, 1.0, 0.2, 0.05)
rating_weight = st.sidebar.slider("Rating Weight", 0.0, 1.0, 0.3, 0.05)

# =========================
# Display helper
# =========================
def display_recommendations(recs):
    """Display top 5 recommendations in podium style with posters and stats."""
    if not recs:
        return

    # Force white text for all markdown/text elements in recommendations
    st.markdown(
        """
        <style>
        .recommendation-text {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    recs = sorted(recs, key=lambda x: x['Similarity'], reverse=True)[:5]

    def show_show(rec):
        st.markdown(f"<h3 class='recommendation-text'>{rec['Name']}</h3>", unsafe_allow_html=True)
        poster_url = df.loc[df['Name'] == rec['Name'], 'Poster_URL'].values
        if len(poster_url) and poster_url[0]:
            st.image(poster_url[0], width=150)
        st.markdown(f"<p class='recommendation-text'>Score: {rec['Similarity']*100:.1f}%</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='recommendation-text'>Director: {rec.get('Director','N/A')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='recommendation-text'>Year: {rec.get('Year','N/A')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='recommendation-text'>Age Rating: {rec.get('Age_Rating','N/A')}</p>", unsafe_allow_html=True)

    # Layout
    col1, col2, col3 = st.columns([2, 4, 2])
    with col2:
        show_show(recs[0])
        st.markdown("---")
    if len(recs) > 1:
        col_left, col_right = st.columns(2)
        with col_left:
            show_show(recs[1])
        if len(recs) > 2:
            with col_right:
                show_show(recs[2])
    if len(recs) > 3:
        col4, col5 = st.columns(2)
        with col4:
            show_show(recs[3])
        if len(recs) > 4:
            with col5:
                show_show(recs[4])

# =========================
# User input
# =========================
user_input = st.text_input("What's your favorite Tokusatsu show?")
selected_title = None
if user_input:
    matches = difflib.get_close_matches(user_input, all_titles, n=5, cutoff=0.6)
    if matches:
        selected_title = st.selectbox("Did you mean one of these?", options=matches, index=0)
    else:
        st.write("No close matches found. Please check your spelling or enter a different title.")

# =========================
# Build similarity matrix
# =========================
feature_matrix = build_feature_matrix(df)
cos_sim = cosine_similarity(feature_matrix)

if st.button("Henshin!"):
    if selected_title:
        try:
            recs = get_recommendations(selected_title, n=5)
            recs = sorted(recs, key=lambda x: x['Similarity'], reverse=True)

            st.write("Here are some recommendations for you:")

            # Backdrop from top-ranked show
            if "Backdrop_URL" in df.columns:
                top_show_backdrop = df.loc[df['Name'] == recs[0]['Name'], 'Backdrop_URL'].values
                if len(top_show_backdrop) and top_show_backdrop[0]:
                    st.markdown(
                        f"""
                        <style>
                        .stApp {{
                            background-image: url('{top_show_backdrop[0]}');
                            background-size: cover;
                            background-attachment: fixed;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

            display_recommendations(recs)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    else:
        st.warning("💡 Enter your favorite Tokusatsu show and confirm a match — then hit Henshin to unleash your recommendations!")