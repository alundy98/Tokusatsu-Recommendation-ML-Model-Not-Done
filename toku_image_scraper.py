import requests
import pandas as pd
import time

API_KEY = "ace66f5714aa2be30f189846996680dd"
BASE_URL = "https://api.themoviedb.org/3"

# Load your existing CSV
df = pd.read_csv("tokusatsu_shows.csv")

def fetch_show_images(show_id):
    """Fetch poster and backdrop paths for a given show ID"""
    url = f"{BASE_URL}/tv/{show_id}"
    params = {"api_key": API_KEY, "language": "en-US"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    
    poster_path = data.get("poster_path")
    backdrop_path = data.get("backdrop_path")
    
    return (
        f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
        f"https://image.tmdb.org/t/p/w780{backdrop_path}" if backdrop_path else None
    )

# Add new columns for poster + backdrop
df["Poster_URL"] = None
df["Backdrop_URL"] = None

print("Fetching image URLs for shows...")
for i, row in df.iterrows():
    poster, backdrop = fetch_show_images(row["ID"])
    df.at[i, "Poster_URL"] = poster
    df.at[i, "Backdrop_URL"] = backdrop
    print(f"✔ {row['Name']} → Poster: {bool(poster)}, Backdrop: {bool(backdrop)}")
    time.sleep(0.25)  # respect API rate limits

# Save back to CSV
df.to_csv("tokusatsu_shows_with_images.csv", index=False, encoding="utf-8")
print("✅ Updated CSV saved as 'tokusatsu_shows_with_images.csv'")
