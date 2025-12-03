# Restaurant Search Module

Semantic search for finding restaurants in a mall using ChromaDB vector store.

## Structure

```
search/
├── data_loader.py    # Load data from Google Sheets, build documents & metadata
└── search.py         # Vector store & search interface
```

## Usage

```python
from search import RestaurantSearch

# Initialize and load data
search = RestaurantSearch(db_path="chromadb")
search.load_and_index()

# Search with filters
results = search.search(
    query="Italian food",
    n_results=3,
    zone="north",
    has_vegan=True
)

# Get specific restaurant
restaurant = search.get_restaurant(restaurant_id=1)
```

## Available Filters

- `price_level`: "low", "medium", "high"
- `zone`: "north", "center", "south"
- `has_vegetarian`, `has_vegan`, `has_gluten_free`
- `has_takeaway`, `has_bar`, `has_menu`
- `allow_reservations`
- `latitude`, `longitude`
- `opening_time`, `closing_time`
