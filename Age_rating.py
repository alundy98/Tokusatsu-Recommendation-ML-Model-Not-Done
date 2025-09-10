import pandas as pd
import re

# Load the CSV with a fallback encoding
df = pd.read_csv(
    "tokusatsu_shows_enriched.csv",
    encoding="utf-8",        # try UTF-8 first
    encoding_errors="replace"  # replace bad bytes with � instead of failing
)

# Function to normalize ratings
def normalize_rating(value):
    if pd.isna(value):
        return 'PG'  # Default if missing

    val = str(value).strip().upper()

    # If there's a number, decide PG or PG13
    match = re.search(r'\d+', val)
    if match:
        num = int(match.group())
        return 'PG' if num < 10 else 'PG13'

    # Specific letter/category mappings
    if val == 'C':
        return 'PG'
    if any(letter in val for letter in ['D', 'S', 'L', 'V']):
        return 'PG13'

    # Direct matches to allowed ratings
    allowed = ['G', 'PG', 'PG13', 'MA', 'TV-MA', 'TV-PG', 'TV-PG13']
    if val in allowed:
        return val

    # Fallback
    return 'PG'

# Apply normalization
df['Age_Rating'] = df['Age_Rating'].apply(normalize_rating)

# Save cleaned CSV
df.to_csv("tokusatsu_shows_enriched_cleaned.csv", index=False)

print("Age_Rating column normalized and saved to tokusatsu_shows_enriched_cleaned.csv")