import requests
import pandas as pd
import time

API_KEY = "ace66f5714aa2be30f189846996680dd"
BASE_URL = "https://api.themoviedb.org/3"

# Load your last CSV (with images, genres, ratings)
df = pd.read_csv("tokusatsu_shows_with_images.csv")


def fetch_extra_details(show_id):
    """Fetch genres, rating, keywords, and main director"""

    # --- Details (genres) ---
    url_details = f"{BASE_URL}/tv/{show_id}"
    r = requests.get(url_details, params={"api_key": API_KEY, "language": "en-US"})
    r.raise_for_status()
    details = r.json()
    genres = [g["name"] for g in details.get("genres", [])]
    genres_str = ", ".join(genres) if genres else None

    # --- Content ratings ---
    url_ratings = f"{BASE_URL}/tv/{show_id}/content_ratings"
    r = requests.get(url_ratings, params={"api_key": API_KEY})
    r.raise_for_status()
    ratings = r.json().get("results", [])
    rating = None
    for item in ratings:
        if item["iso_3166_1"] == "US":
            rating = item["rating"]
            break
    if not rating and ratings:
        rating = ratings[0]["rating"]

    # --- Keywords ---
    url_keywords = f"{BASE_URL}/tv/{show_id}/keywords"
    r = requests.get(url_keywords, params={"api_key": API_KEY})
    r.raise_for_status()
    keywords = [k["name"] for k in r.json().get("results", [])]
    keywords_str = ", ".join(keywords) if keywords else None

    # --- Directors (pick the one with most episodes) ---
    url_credits = f"{BASE_URL}/tv/{show_id}/aggregate_credits"
    r = requests.get(url_credits, params={"api_key": API_KEY})
    r.raise_for_status()
    crew = r.json().get("crew", [])
    directors = [c for c in crew if c.get("job") == "Director"]
    main_director = None
    if directors:
        # pick the one with max episodes
        main_director = max(directors, key=lambda d: d.get("total_episode_count", 0)).get("name")

    return genres_str, rating, keywords_str, main_director

# Add new columns
df["Genres"] = None
df["Age_Rating"] = None
df["Keywords"] = None
df["Director"] = None

print("Fetching genres, ratings, keywords & directors...")
for i, row in df.iterrows():
    try:
        genres, rating, keywords, director = fetch_extra_details(row["ID"])
        df.at[i, "Genres"] = genres
        df.at[i, "Age_Rating"] = rating
        df.at[i, "Keywords"] = keywords
        df.at[i, "Director"] = director
        print(f"✔ {row['Name']} → Genres: {genres}, Rating: {rating}, Director: {director}")
    except Exception as e:
        print(f"⚠ Error on {row['Name']} ({row['ID']}): {e}")
    time.sleep(0.3)  # be gentle on API

# Save updated CSV
df.to_csv("tokusatsu_shows_enriched.csv", index=False, encoding="utf-8")
print("✅ Updated CSV saved as 'tokusatsu_shows_enriched.csv'")
