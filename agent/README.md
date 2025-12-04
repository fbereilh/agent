# Restaurant Agent Module

Conversational AI agent for restaurant recommendations using Lisette for LLM calls and integrated search tools.

## Structure

```
agent/
├── agent.py           # Chat agent with search & location tools
└── system_prompt.txt  # Dynamic system prompt template
```

## Features

- **Context-aware prompts**: Adapts to current time (Madrid timezone) and meal periods (breakfast 7-11, lunch 13-16, dinner 19-22)
- **Three search tools**: Restaurant search, dish search, and walking time calculator
- **Spanish language**: Natural, friendly conversation style with automatic welcome message
- **Tool calling**: Automatically uses search_restaurants, search_dishes, and get_walking_time
- **Rich filtering**: Price levels, zones, dietary restrictions, opening hours, and more

## Usage

```python
from agent import RestaurantAgent

# Initialize
agent = RestaurantAgent(db_path="chromadb")

# Chat (agent starts with a Spanish welcome message)
response = agent("Quiero un italiano para cenar")
print(response)

# Search for specific dishes
response = agent("¿Dónde puedo encontrar tiramisú?")

# Check walking times
response = agent("¿Cuánto se tarda en caminar de un restaurante a otro?")

# History
print(agent.history)
```

## Tools

### search_restaurants
Searches restaurants by query with filters:
- `query`: Natural language search (required)
- `n_results`: Number of results (default: 3)
- `price_level`: "low", "medium", "high"
- `zone`: "north", "center", "south"
- `has_vegan`, `has_vegetarian`, `has_gluten_free`: Boolean dietary filters
- `has_takeaway`, `has_bar`, `has_menu`, `allow_reservations`: Boolean service filters
- `open_now`: Boolean, filters currently open restaurants
- `open_at_time`: String format "HH:MM" (e.g., "14:30")

Returns formatted restaurant information with descriptions, cuisine types, dietary options, menu highlights, location, services, hours, and contact details.

### search_dishes
Searches for specific dishes across all restaurants:
- `query`: Natural language dish search (required)
- `n_results`: Number of results (default: 5)
- `restaurant_name`: Filter by specific restaurant
- `zone`: "north", "center", "south"
- `price_level`: "low", "medium", "high"
- `has_vegetarian`, `has_vegan`, `has_gluten_free`, `has_halal`, `has_lactose_free`: Boolean dietary filters
- `category`: Filter by dish category

Returns dish information grouped by restaurant with location details. Use this when users ask about specific dishes rather than general restaurant recommendations.

### get_walking_time
Calculates walking time between two restaurants:
- `from_restaurant`: Starting restaurant name (required)
- `to_restaurant`: Destination restaurant name (required)

Returns estimated walking time in minutes (rounded to 1 decimal place). Uses mall-calibrated walking speed of 69 meters per minute.

## Configuration

```python
agent = RestaurantAgent(
    model="claude-haiku-4-5-20251001",  # LLM model (or set AGENT_MODEL env var)
    temp=0.5,                            # Temperature
    db_path="chromadb"                   # Search DB path
)
```

## System Prompt

The agent uses a dynamic system prompt that includes:
- Current date and time in Madrid timezone
- Contextual meal period information (breakfast/lunch/dinner)
- Loaded from `system_prompt.txt` template

## Welcome Message

On initialization, the agent automatically adds a Spanish welcome message explaining its capabilities for restaurant recommendations, dietary options, locations, prices, and hours.