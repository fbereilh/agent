# Restaurant Agent Module

Conversational AI agent for restaurant recommendations using Lisette for LLM calls and integrated search tools.

## Structure

```
agent/
└── agent.py    # Chat agent with search & location tools
```

## Features

- **Context-aware prompts**: Adapts to current time and meal periods
- **Search tool**: Semantic search with filters (price, dietary, zone)
- **Walking time tool**: Calculate distances between restaurants
- **Spanish language**: Natural, friendly conversation style
- **Tool calling**: Uses search_restaurants and get_walking_time automatically

## Usage

```python
from agent import RestaurantAgent

# Initialize
agent = RestaurantAgent(db_path="chromadb")

# Chat
response = agent("Quiero un italiano para cenar")
print(response)

# History
print(agent.history)
```

## Tools

### search_restaurants
Searches restaurants by query with filters:
- `query`: Natural language search
- `price_level`: "low", "medium", "high"
- `zone`: "north", "center", "south"
- `has_vegan`, `has_vegetarian`, `has_gluten_free`
- `has_takeaway`, `has_bar`, `has_menu`
- `open_now`, `open_at_time`

### get_walking_time
Calculates walking time between restaurants using coordinates and mall walking speed (69 m/min).

## Configuration

```python
agent = RestaurantAgent(
    model="claude-haiku-4-5-20251001",  # LLM model
    temp=0.5,                            # Temperature
    db_path="chromadb"                   # Search DB path
)
```
