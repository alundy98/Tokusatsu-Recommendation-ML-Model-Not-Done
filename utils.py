import pandas as pd
import numpy as np
def get_season(title: str) -> str:
    if "Season" in title:
        return title.split("Season")[0].strip()
    return "Unknown"

def get_keywords(description: str) -> list:
    if pd.isna(description):
        return []
    keywords = [kw.strip() for kw in description.split(",")]
    return [kw for kw in keywords if kw]

def get_numeric_features(df):
    num = ['Year', 'Num Episodes', 'Avg Episode Duration', 'Num Main Cast', 'Num Directors']
    x_num = df[num]
    return x_num
