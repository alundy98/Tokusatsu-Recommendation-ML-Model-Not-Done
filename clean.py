import pandas as pd

#load dataset
df = pd.read_csv("tokusatsu_shows_enriched.csv")
print("before cleaning:")
print(df.info())
print(df.head(3))

#remove duplicates
df = df.drop_duplicates()

#fill nans for text columns
df['Overview'] = df['Overview'].fillna("No summary available")
df['Age_Rating'] = df['Age_Rating'].fillna("PG")
df['Director'] = df['Director'].fillna("Unknown")
df['Genres'] = df['Genres'].fillna("")
df['Keywords'] = df['Keywords'].fillna("")

#convert first air date
df['First Air Date'] = pd.to_datetime(df['First Air Date'], errors='coerce')

#convert numeric columns
df['Popularity'] = pd.to_numeric(df['Popularity'], errors='coerce')
df['Vote Average'] = pd.to_numeric(df['Vote Average'], errors='coerce')
df['Vote Count'] = pd.to_numeric(df['Vote Count'], errors='coerce')

#slots in median for missing numeric values
for col in ['Popularity','Vote Average','Vote Count']:
    median_val = df[col].median(skipna=True)
    df[col] = df[col].apply(lambda x: median_val if pd.isna(x) or x == 0 else x)

#genres/keywords to lists
df['Genres'] = df['Genres'].apply(lambda x: [g.strip() for g in str(x).split(",") if g.strip()])
df['Keywords'] = df['Keywords'].apply(lambda x: [k.strip() for k in str(x).split(",") if k.strip()])

#normalize age ratings
def normalize_rating(r):
    if pd.isna(r) or r.strip() == "":
        return "PG"
    r = str(r).upper()
    if "PG-13" in r: return "PG-13"
    if "PG" in r: return "PG"
    if "R" in r: return "R"
    if "G" in r: return "G"
    return "PG"
df['Age_Rating'] = df['Age_Rating'].apply(normalize_rating)

#actual display title
df['full_title'] = (
    df['Name'].astype(str).str.strip()
    + " (" + df['First Air Date'].dt.year.fillna(0).astype(int).astype(str) + ")"
)

#normalize numeric columns to [0,1]
for col in ['Popularity','Vote Average','Vote Count']:
    col_min, col_max = df[col].min(), df[col].max()
    if col_max != col_min:
        df[col] = (df[col] - col_min) / (col_max - col_min)
    else:
        df[col] = 0.5
print("after cleaning:")
print(df.info())
print(df.head(3))

df.to_csv("tokusatsu_clean.csv", index=False)
