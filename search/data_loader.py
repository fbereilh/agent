"""Data loading and document building functionality for restaurant and dish data."""

import httpx
import pandas as pd
from io import BytesIO
from typing import Dict, Tuple, Any


SHEET_ID = "13h-DvmpyZSa522PVam7rmqcbAXwuB3blSkKye4Wx6qc"


def load_restaurant_data(sheet_id: str = SHEET_ID) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load restaurant and dish data from Google Sheets.
    
    Args:
        sheet_id: Google Sheets ID to load data from
        
    Returns:
        Tuple of (restaurants_df, dishes_df) DataFrames
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    r = httpx.get(url, follow_redirects=True)
    sheets = pd.read_excel(BytesIO(r.content), sheet_name=None)
    
    df_restaurants = sheets['restaurants']
    
    # Handle dishes - merge restaurant_dishes with dish_keywords and restaurant names
    if 'restaurant_dishes' in sheets and 'dish_keywords' in sheets:
        cols = ['restaurant_id', 'dish_id', 'weight', 'updated_at']
        df_rest_dishes = sheets['restaurant_dishes'][cols]
        
        df_dishes = df_rest_dishes.merge(
            sheets['dish_keywords'], 
            left_on='dish_id', 
            right_on='id',
            suffixes=('', '_dish')
        ).merge(
            sheets['restaurants'][['id', 'name']], 
            left_on='restaurant_id', 
            right_on='id',
            suffixes=('', '_rest')
        )
        
        # Sort by restaurant and weight (descending)
        df_dishes = df_dishes.sort_values(['restaurant_id', 'weight'], ascending=[True, False])
    else:
        # Empty DataFrame if no dishes available
        df_dishes = pd.DataFrame()
    
    # Add zone and location data if missing
    zone_data = {
        'Andreu': {'zone': 'north', 'lat': 41.613362, 'lng': 2.345123},
        'Atmósferas Mordisco': {'zone': 'center', 'lat': 41.610738, 'lng': 2.343823},
        'Corso Iluzione': {'zone': 'south', 'lat': 41.608389, 'lng': 2.342116},
        'Centric': {'zone': 'north', 'lat': 41.611688, 'lng': 2.344386},
        'Dino': {'zone': 'north', 'lat': 41.611700, 'lng': 2.344400},
        'Farggi 1957': {'zone': 'south', 'lat': 41.608412, 'lng': 2.342555},
        'Mori by Parco': {'zone': 'north', 'lat': 41.612212, 'lng': 2.345061},
        'Starbucks': {'zone': 'center', 'lat': 41.610216, 'lng': 2.343253},
        'Waff (Ice Pops)': {'zone': 'center', 'lat': 41.609468, 'lng': 2.342820},
        'Lindt': {'zone': 'center', 'lat': 41.610858, 'lng': 2.344183},
        'Fire & Bread': {'zone': 'center', 'lat': 41.610417, 'lng': 2.343262},
        'Gasso': {'zone': 'south', 'lat': 41.608751, 'lng': 2.342281},
        'Izky Noodles': {'zone': 'south', 'lat': 41.609422, 'lng': 2.342783},
        'Rocambolesc': {'zone': 'north', 'lat': 41.611882, 'lng': 2.344658},
    }
    
    if 'zone' not in df_restaurants.columns:
        df_restaurants['zone'] = None
    if 'lat' not in df_restaurants.columns:
        df_restaurants['lat'] = None
    if 'lng' not in df_restaurants.columns:
        df_restaurants['lng'] = None
    
    for idx, row in df_restaurants.iterrows():
        if row['name'] in zone_data:
            df_restaurants.at[idx, 'zone'] = zone_data[row['name']]['zone']
            df_restaurants.at[idx, 'lat'] = zone_data[row['name']]['lat']
            df_restaurants.at[idx, 'lng'] = zone_data[row['name']]['lng']
    
    return df_restaurants, df_dishes
    
    return df_restaurants, df_dishes


def load_all_sheets(sheet_id: str = SHEET_ID) -> Dict[str, pd.DataFrame]:
    """
    Load all sheets from Google Sheets.
    
    Args:
        sheet_id: Google Sheets ID to load data from
        
    Returns:
        Dictionary mapping sheet names to DataFrames
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    r = httpx.get(url, follow_redirects=True)
    sheets = pd.read_excel(BytesIO(r.content), sheet_name=None)
    return sheets


def make_restaurant_doc_with_dishes(row: pd.Series, df_dishes: pd.DataFrame, top_n: int = 10) -> str:
    """
    Create a searchable description for a restaurant with top dishes.
    
    Args:
        row: Restaurant row from DataFrame
        df_dishes: DataFrame with all dishes
        top_n: Number of top dishes to include
        
    Returns:
        Formatted restaurant document string
    """
    # Base restaurant info
    parts = [
        f"{row['name']} is a {row['price_level']}-priced restaurant",
        f"located in the {row.get('zone', '')} zone of the mall." if pd.notna(row.get('zone')) else ".",
        row['description_long'] or row['description_short'],
        f"Cuisine types: {row.get('cuisines')}." if pd.notna(row.get('cuisines')) else "",
        f"Dietary options available: {row.get('dietary_tags')}." if pd.notna(row.get('dietary_tags')) else "",
        f"Services: {row.get('services')}." if pd.notna(row.get('services')) else "",
        f"Open {row.get('opening_hours')}." if pd.notna(row.get('opening_hours')) else "",
    ]
    
    # Get top dishes for this restaurant
    rest_dishes = df_dishes[df_dishes['restaurant_id'] == row['id']].head(top_n)
    
    if len(rest_dishes) > 0:
        parts.append("\nMenu highlights:")
        for _, dish in rest_dishes.iterrows():
            dish_text = dish.get('text', dish.get('name', 'Unknown dish'))
            # Add dietary tags to each dish if available
            if pd.notna(dish.get('dietary_tags')):
                dish_text += f" ({dish.get('dietary_tags')})"
            parts.append(f"- {dish_text}")
    
    return " ".join(p for p in parts if p)


def make_metadata(row: pd.Series) -> Dict[str, Any]:
    """
    Create metadata dictionary for a restaurant.
    
    Args:
        row: Restaurant row from DataFrame
        
    Returns:
        Dictionary with restaurant metadata
    """
    # Parse opening hours
    opening_time = ""
    closing_time = ""
    if pd.notna(row.get('opening_hours')) and '-' in str(row.get('opening_hours')):
        times = str(row.get('opening_hours')).split('-')
        opening_time = times[0].strip()
        closing_time = times[1].strip()
    
    return {
        "restaurant_id": int(row['id']),
        "name": row['name'],
        "price_level": row.get('price_level', ''),
        "zone": row.get('zone', '') if pd.notna(row.get('zone')) else "",
        "latitude": float(row.get('lat', 0)) if pd.notna(row.get('lat')) else 0.0,
        "longitude": float(row.get('lng', 0)) if pd.notna(row.get('lng')) else 0.0,
        "has_vegetarian": "vegetarian" in str(row.get('dietary_tags', '')).lower(),
        "has_vegan": "vegan" in str(row.get('dietary_tags', '')).lower(),
        "has_gluten_free": "gluten_free" in str(row.get('dietary_tags', '')).lower(),
        "has_menu": bool(row.get('has_menu', False)),
        "allow_reservations": bool(row.get('allow_reservations', False)),
        "has_takeaway": "takeaway" in str(row.get('services', '')).lower(),
        "has_bar": "bar" in str(row.get('services', '')).lower(),
        "phone": row.get('phone', ''),
        "website_url": row.get('website_url', ''),
        "opening_time": opening_time,
        "closing_time": closing_time,
    }
