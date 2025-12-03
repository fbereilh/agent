# Restaurant Recommendation Agent

An intelligent agent system for helping users find restaurants in a mall using semantic search, conversational AI, and a modern web interface.

## Project Overview

This project implements a restaurant recommendation system with the following features:
- **Semantic Search**: Find restaurants using natural language queries
- **Chat Agent**: Conversational interface for personalized recommendations
- **Web UI**: User-friendly interface built with FastHTML and DaisyUI
- **Monitoring**: Track usage and system performance

## Technology Stack

- **Backend & Frontend**: FastHTML with DaisyUI
- **Vector Store**: ChromaDB (SQLite-based)
- **LLM Integration**: Lisette for chat management
- **Data Storage**: FastLite (if needed for additional database needs)
- **Data Source**: Google Sheets

## Project Structure

```
.
├── search/                 # ✅ Search module (Step 1 - Complete)
│   ├── __init__.py
│   ├── data_loader.py     # Load data from Google Sheets
│   ├── document_builder.py # Create searchable documents
│   ├── vector_store.py    # ChromaDB management
│   ├── search_interface.py # High-level search API
│   └── README.md          # Search module documentation
├── chat/                   # 🚧 Chat agent module (Step 2 - TODO)
├── ui/                     # 🚧 Web interface (Step 3 - TODO)
├── monitoring/             # 🚧 Monitoring functionality (Step 4 - TODO)
├── example_search.py      # Example usage of search module
├── main.py                # Main application entry point
├── 00_core.ipynb          # Development notebook
├── pyproject.toml         # Project dependencies
└── README.md              # This file
```

## Development Roadmap

### ✅ Step 1: Search Feature (Complete)
A modular search system for semantic restaurant discovery.

**Key Features:**
- Natural language search queries
- Metadata filtering (price, zone, dietary options)
- Integration with top dishes
- Persistent vector store

**See:** [`search/README.md`](search/README.md) for detailed documentation.

### 🚧 Step 2: Chat Agent (TODO)
Conversational interface for restaurant recommendations using Lisette.

**Planned Features:**
- Natural conversation flow
- Context-aware recommendations
- Multi-turn dialogues
- Integration with search module

### 🚧 Step 3: Web UI (TODO)
User-friendly web interface using FastHTML and DaisyUI.

**Planned Features:**
- Restaurant browsing
- Search interface
- Chat widget
- Responsive design

### 🚧 Step 4: Monitoring (TODO)
Analytics and monitoring functionality.

**Planned Features:**
- Usage tracking
- Search analytics
- Performance metrics
- User interaction logs

## Installation

### Prerequisites
- Python 3.12+
- UV package manager

### Setup

1. Clone the repository
```bash
cd agent
```

2. Install dependencies
```bash
uv sync
```

3. Run the search example
```bash
uv run python example_search.py
```

## Quick Start

### Using the Search Module

```python
from search import RestaurantSearch

# Initialize search
search = RestaurantSearch(db_path="chromadb")
search.load_and_index()

# Search for restaurants
results = search.search(
    query="Italian food with vegan options",
    n_results=3,
    has_vegan=True
)

for result in results:
    print(f"{result['metadata']['name']} - {result['metadata']['zone']}")
```

## Development

### Working with Notebooks

The project includes `00_core.ipynb` for interactive development and experimentation.

### Adding Dependencies

```bash
uv add package-name
```

### Running Tests

```bash
# To be implemented
```

## Data Source

Restaurant and dish data is loaded from a Google Sheets document. The data includes:
- Restaurant information (name, description, location, hours, etc.)
- Menu items and dishes
- Dietary tags and options
- Pricing information
- Services offered

## Contributing

This is a learning/demonstration project. Contributions and suggestions are welcome!

## License

[To be determined]

## Next Steps

1. ✅ Implement search functionality
2. 🚧 Develop chat agent module
3. 🚧 Build web UI
4. 🚧 Add monitoring capabilities

---

**Current Status:** Step 1 (Search Feature) completed. Ready for Step 2 (Chat Agent).
