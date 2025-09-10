import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack, csr_matrix

# =========================
# Load data safely
# =========================
try:
    df = pd.read_csv("tokusatsu_shows_enriched_cleaned.csv", encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv("tokusatsu_shows_enriched_cleaned.csv", encoding="latin1")
# Create full_title for matching
df["Year"] = pd.to_datetime(df["First Air Date"], errors="coerce").dt.year
df["full_title"] = df["Name"].fillna("") + " (" + df["Year"].fillna(0).astype(int).astype(str) + ")"

# =========================
# Helpers
# =========================
def parse_list_column(col):
    def parse(x):
        if pd.isna(x):
            return []
        if isinstance(x, list):
            return [s.strip() for s in x]
        if isinstance(x, str):
            return [s.strip().strip("'\"") for s in x.strip("[]").split(",") if s.strip()]
        return []
    return col.apply(parse)

def normalize_title(s):
    return re.sub(r'\s+', ' ', str(s).strip().lower()) if pd.notna(s) else ''

special_directors = {
    "naruhisa arakawa","shozo uehara","keiichi hasegawa","yasuko kobayashi",
    "toshiki inoue","sho aikawa","yuji kobayashi","seiji takaiwa","hirofumi fukuzawa",
    "kazuo niibori","eiji tsuburaya","shotaro ishinomori","saburo yatsude",
    "shotaro moriyasu","takao nagaishi","koichi takemoto","takashi miike",
    "hiroshi miyauchi","kazup niibori","kenji ohba"
}

# =========================
# Feature builder
# =========================
def build_feature_matrix(df, weights=None):
    if weights is None:
        weights = {
            "overview": 2.0,
            "age_rating": 2.0,
            "genres": 4.0,
            "keywords": 5.0,
            "director": 4.0,
            "popularity": 1.0,
            "vote_avg": 1.0,
            "vote_count": 0.5
        }

    df = df.copy()
    df["parsed_genres"] = parse_list_column(df["Genres"])
    df["parsed_keywords"] = parse_list_column(df["Keywords"])
    df["director_clean"] = df["Director"].fillna("Unknown").astype(str)

    # Overview TF-IDF
    tfidf = TfidfVectorizer(stop_words="english")
    x_overview = tfidf.fit_transform(df["Overview"].fillna(""))

    # Genres
    mlb_g = MultiLabelBinarizer()
    x_genres = csr_matrix(mlb_g.fit_transform(df["parsed_genres"]).astype(np.float32))

    # Keywords
    mlb_k = MultiLabelBinarizer()
    x_keywords = csr_matrix(mlb_k.fit_transform(df["parsed_keywords"]).astype(np.float32))

    # Director one-hot + bonus
    x_dir_df = pd.get_dummies(df["director_clean"], prefix="dir")
    bonus_mask = x_dir_df.columns.str.lower().map(lambda d: any(sd in d for sd in special_directors))
    if bonus_mask.any():
        x_dir_df["dir_bonus"] = x_dir_df.loc[:, bonus_mask].sum(axis=1)
    x_dir = csr_matrix(x_dir_df.values.astype(np.float32))

    # Age Rating
    x_age = csr_matrix(pd.get_dummies(df["Age_Rating"].fillna("Unknown"), prefix="age").values.astype(np.float32))

    # Numeric features
    num_feats = df[["Popularity", "Vote Average", "Vote Count"]].fillna(0)
    scaler = MinMaxScaler()
    x_num = csr_matrix(scaler.fit_transform(num_feats).astype(np.float32))

    # Weighted hstack
    feats = [
        x_overview * weights["overview"],
        x_age * weights["age_rating"],
        x_genres * weights["genres"],
        x_keywords * weights["keywords"],
        x_dir * weights["director"],
        x_num[:, 0] * weights["popularity"],
        x_num[:, 1] * weights["vote_avg"],
        x_num[:, 2] * weights["vote_count"]
    ]
    return hstack(feats, format="csr")

# =========================
# Build similarity
# =========================
feature_matrix = build_feature_matrix(df)
cosine_sim = cosine_similarity(feature_matrix)

# =========================
# Recommender
# =========================
def get_recommendations(title, n=5):
    matches = df.index[df['full_title'].str.lower() == title.lower()]
    if not len(matches):
        raise ValueError(f"'{title}' not found in dataset.")
    idx = matches[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    results = []
    for i, score in sorted(sim_scores, key=lambda x: x[1], reverse=True):
        if i == idx:
            continue
        name_a = normalize_title(df.loc[idx, "Name"])
        name_b = normalize_title(df.loc[i, "Name"])
        if name_a.split()[0] in name_b or name_b.split()[0] in name_a:
            score += 0.2
        results.append({
            "Name": df.loc[i, "Name"],
            "Similarity": round(float(score), 4),
            "Director": df.loc[i, "Director"],
            "Year": df.loc[i, "Year"],
            "Age_Rating": df.loc[i, "Age_Rating"]
        })
        if len(results) >= n:
            break
    return results

# =========================
# Example
# =========================
print(get_recommendations("GARO (2005)", n=5))