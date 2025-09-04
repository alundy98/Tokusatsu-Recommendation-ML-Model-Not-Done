import os
import re
import numpy as np
import pandas as pd
import warnings
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option("display.max_columns", None)
warnings.filterwarnings("ignore")
warnings.filterwarnings("always")

# Load data
data_path = r"C:\Users\alecl\OneDrive\Desktop\AL REPOS\TokuProject.csv"
df = pd.read_csv(data_path)

#load data and some cleaning add back the rest later for a note
df = df.drop_duplicates()
df = df[df['Part. Rate %'].notna()]
df['Keywords'] = df['Keywords'].fillna(df['Keywords'].dropna().mode().values[0])
df['Series'] = df['Series'].fillna(df['Series'].dropna().mode().values[0])
df['Director'] = df['Director'].fillna(df['Director'].dropna().mode().values[0])

quant = ['Avg. Rating (- Outliers)', 'Part. Rate %', 'Season SD']

# quantatative vals
x_num = df[quant].copy()

# If Part. Rate % still has '%' symbols, strip  and convert to float
if df['Part. Rate %'].dtype == 'object':
    x_num['Part. Rate %'] = x_num['Part. Rate %'].str.rstrip('%').astype(float)
x_num = x_num.fillna(x_num.mean())

# Nonrmalize=
x_num = (x_num - x_num.min()) / (x_num.max() - x_num.min())

X_num = x_num.fillna(x_num.mean())

print(X_num.head())
#One-Hot Encode Categorical Features
cat = ['Series', 'Era', 'Director', 'Production Company']
x_cat = pd.get_dummies(df[cat], prefix=cat, dummy_na=False)

#Multi- hot 
keyword_pool = [
    'Dark', 'Apocalypse', 'Survival Game', 'Post-Apocalypse', 'Evil Organization',
    'Time Travel', 'Dramatic', 'Mystery', 'Urban', 'Monsters',
    'Space', 'Lighthearted', 'Legacy Factor', 'Aliens',
    'Nature', 'Brooding', 'Gaming', 'Belt', 'Corporate/Science',
    'Rival Riders', 'War', 'Mythology', 'Futuristic', 'Detective',
    'Strong Team', 'School', 'Demons', 'Cheerful', 'Alternate Dimensions',
    'Coming of Age', 'Serious', 'Comedy', 'Magic', 'Fantasy'
]

# Split keywords, clean spaces, remove empty strings
kw = df['Keywords'].fillna("").str.split(",").apply(lambda x: [k.strip() for k in x if k.strip() != ""])

# Initialize multi-hot DataFrame
x_kw = pd.DataFrame(0, index=df.index, columns=keyword_pool, dtype=int)
#Creating full title category
df['Series'] = df['Series'].astype(str).fillna('').str.strip()
df['Season'] = df['Season'].astype(str).fillna('').str.strip()
df['full_title'] = (df['Series'] + ' ' + df['Season']).str.strip()

# normalization helper: lowercase + collapse whitespace
def normalize_title(s):
    if pd.isna(s):
        return ''
    s = str(s).strip().lower()
    s = re.sub(r'\s+', ' ', s)   # collapse multiple spaces into one
    return s
# normalized column to match against (compute once)
df['full_title_norm'] = df['full_title'].apply(normalize_title)

def get_all_full_titles():
    return df['full_title'].dropna().unique().tolist()

# Fill multi-hot matrix
for i, keywords in enumerate(kw):
    for keyword in keywords:
        if keyword in keyword_pool:
            x_kw.loc[i, keyword] = 1

#easy big matrix to just call it instead of all 3
x_fin = pd.concat([x_num, x_cat, x_kw], axis=1).fillna(0)


#cosine_similarity from sklearn.metrics.pairwise used
cosine_sim = cosine_similarity(x_fin)

def get_top5_recommendations(show_title, n=5, max_per_series=3):
    """
    Returns top N Tokusatsu recommendations as a list of dictionaries:
    Each dict contains: Series, Season, Similarity, Rating, Era
    """
    show_title = show_title.strip().lower()  # normalize input

    # Find matching full_title in df
    matches = df.index[df['full_title'].str.lower() == show_title]

    if len(matches) == 0:
        # fallback: partial match (so user can type "kamen rider w" etc.)
        matches = df.index[df['full_title'].str.lower().str.contains(show_title)]

    if len(matches) == 0:
        raise ValueError(f"Show '{show_title}' not found. Please use exact full title or select from suggestions.")

    target_idx = matches[0]

    # Get similarity scores for all shows
    sims = list(enumerate(cosine_sim[target_idx]))
    sims = sorted(sims, key=lambda x: x[1], reverse=True)[1:]  # exclude the show itself

    recommendations = []
    series_counts = {}

    for idx, score in sims:
        series = df.loc[idx, "Series"]
        season = df.loc[idx, "Season"]

        # enforce max_per_series rule
        if series_counts.get(series, 0) >= max_per_series:
            continue

        # build dictionary with extra stats
        rec_dict = {
            "Series": series,
            "Season": season,
            "Similarity": score,
            "Rating": df.loc[idx].get("Avg. Rating (- Outliers)", "N/A"),
            "Era": df.loc[idx].get("Era", "N/A")
        }

        recommendations.append(rec_dict)
        series_counts[series] = series_counts.get(series, 0) + 1

        if len(recommendations) >= n:
            break

    return recommendations



