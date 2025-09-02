import os
import numpy as np
import pandas as pd
import warnings
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option("display.max_columns", None)
warnings.filterwarnings("ignore")
warnings.filterwarnings("always")

# List all files (for debug ig)
for dirname, _, filenames in os.walk(r'C:\Users\alecl\OneDrive\Desktop\AL REPOS'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
# Load data
data_path = r'C:\Users\alecl\OneDriv e\Desktop\AL REPOS\TokuProject.csv'
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

# Fill multi-hot matrix
for i, keywords in enumerate(kw):
    for keyword in keywords:
        if keyword in keyword_pool:
            x_kw.loc[i, keyword] = 1

#easy big matrix to just call it instead of all 3
x_fin = pd.concat([x_num, x_cat, x_kw], axis=1).fillna(0)


#cosine_similarity from sklearn.metrics.pairwise used
cosine_sim = cosine_similarity(x_fin)   

def get_top5_recommendations(series, show_title, n=5, max_per_series=3):
    # find the row for the target season
    matches = df.index[df['Season'] == show_title]
    if len(matches) == 0:
        raise ValueError(f"Show '{show_title}' not found")
    idx = matches[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # removes the show we are matching with
    sim_scores = sim_scores[1:]
    results = []
    series_count = {}
    for i, score in sim_scores:
        s = df.loc[i, "Series"]
        if series_count.get(s, 0) < max_per_series:
            results.append({
                "Series": s,
                "Season": df.loc[i, "Season"],
                "Similarity": round(score, 3)
            })
            series_count[s] = series_count.get(s, 0) + 1
        if len(results) >= n:
            break
    return results

print(get_top5_recommendations('Power Rangers', "Time Force" , n=5))