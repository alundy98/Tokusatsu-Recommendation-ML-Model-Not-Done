import pandas as pd

df = pd.read_csv("tokusatsu_shows_enriched.csv")

print(df.info())
print(df.head(3))
df = df.drop_duplicates()

# Fill NaNs
df['Overview'] = df['Overview'].fillna("No summary available")
df['Age_Rating'] = df['Age_Rating'].fillna("Unrated")
df['Director'] = df['Director'].fillna("Unknown")
df['Genres'] = df['Genres'].fillna("")
df['Keywords'] = df['Keywords'].fillna("")
# Convert date
df['First Air Date'] = pd.to_datetime(df['First Air Date'], errors='coerce')

# Numeric conversions
df['Popularity'] = pd.to_numeric(df['Popularity'], errors='coerce')
df['Vote Average'] = pd.to_numeric(df['Vote Average'], errors='coerce')
df['Vote Count'] = pd.to_numeric(df['Vote Count'], errors='coerce')

# Split genres/keywords into lists
df['Genres'] = df['Genres'].apply(lambda x: [g.strip() for g in str(x).split(",") if g.strip()])
df['Keywords'] = df['Keywords'].apply(lambda x: [k.strip() for k in str(x).split(",") if k.strip()])

# Standardize Age Ratings (e.g. "TV-PG" → "PG")
def normalize_rating(r):
    if pd.isna(r): return "Unrated"
    r = str(r).upper()
    if "PG-13" in r: return "PG-13"
    if "PG" in r: return "PG"
    if "R" in r: return "R"
    if "G" in r: return "G"
    return "Unrated"

df['Age_Rating'] = df['Age_Rating'].apply(normalize_rating)
# Create display title
df['full_title'] = df['Name'].astype(str).str.strip() + " (" + df['First Air Date'].dt.year.astype(str) + ")"

# Normalize popularity & ratings
for col in ['Popularity', 'Vote Average', 'Vote Count']:
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
df.to_csv("tokusatsu_clean.csv", index=False)
