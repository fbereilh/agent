# Restaurant Recommendation Agent

An intelligent conversational agent for a shopping mall that helps visitors find the perfect restaurant using semantic search, AI-powered chat, and real-time streaming responses.

## Project Overview

This project implements a complete restaurant recommendation system for La Roca Village mall with:
- **Semantic Search**: Vector-based search across 16 restaurants and 697 dishes with natural language queries
- **Dish Search**: Dedicated search for specific dishes (pasta, tiramisu, vegan options) across all restaurants
- **AI Chat Agent**: Conversational interface with 3 tool calling capabilities for dynamic recommendations
- **Streaming Web UI**: Real-time response streaming with FastHTML and DaisyUI
- **Location Intelligence**: Walking time calculations between restaurants

## Development Approach

This project was developed using a **notebook-first workflow** where all experimentation, prototyping, and testing was done in `00_develop.ipynb`. The production modules were then structured and refined with AI assistance to maintain consistency with the notebook implementation.

**Workflow:**
1. **Exploration Phase**: Data analysis, vector store setup, and tool design in Jupyter notebook
2. **Modularization**: Code extracted into proper Python modules (`search/`, `agent/`)
3. **UI Development**: FastHTML web interface with server-sent events for streaming
4. **AI-Assisted Refinement**: GitHub Copilot used to ensure consistency between notebook and production code

## Technology Stack

- **Backend & Frontend**: FastHTML with DaisyUI v5 + Tailwind Browser v4
- **Vector Store**: ChromaDB with dual collections (restaurants + dishes) for semantic search
- **LLM Integration**: Lisette + LiteLLM with Anthropic Claude (Haiku 4.5)
- **Streaming**: Server-Sent Events (SSE) for real-time response rendering
- **Data Source**: Google Sheets (16 restaurants, 697 dishes with metadata)
- **Package Management**: uv for fast, reliable Python dependency management
- **Container Runtime**: Docker/Podman support for deployment

## Project Structure

```
.
├── 00_develop.ipynb       # Development notebook (original source of truth)
├── search/                # ✅ Search module (Step 1 - Complete)
│   ├── data_loader.py     # Google Sheets data loading and document building
│   ├── search.py          # Vector store + search interface with singleton pattern
│   └── README.md
├── agent/                 # ✅ Chat agent module (Step 2 - Complete)
│   ├── agent.py           # RestaurantAgent with search & walking time tools
│   ├── system_prompt.txt  # Spanish language system prompt
│   └── README.md
├── tests/                 # ✅ Test suite
│   ├── search.py          # Search module tests (all passing)
│   └── agent.py           # Agent module tests (2 passing, 1 requires API key)
├── main.py                # ✅ FastHTML web app with streaming (Step 3 - Complete)
├── styles.css             # Custom oklch color theme for DaisyUI
├── .env.example           # Environment variables template
├── pyproject.toml         # uv project dependencies
└── README.md              # This file
```

## Development Roadmap

### ✅ Step 1: Search Feature (Complete)
Semantic search system for restaurant and dish discovery.

**Implementation:**
- `search/data_loader.py`: Load from Google Sheets, build searchable documents with top dishes
- `search/search.py`: ChromaDB with dual vector stores (restaurants + dishes)
  - RestaurantVectorStore: 16 restaurants indexed with 13 metadata filters
  - DishVectorStore: 697 dishes indexed with dietary tags and restaurant context
- Singleton pattern for efficient search instance reuse
- Persistent vector store with separate collections

**Key Features:**
- Restaurant search with zone, price, dietary filters
- Dish-specific search across all restaurants
- Dietary tag filtering (vegan, vegetarian, gluten-free, halal, lactose-free)
- Restaurant metadata enrichment in dish results

**See:** [`search/README.md`](search/README.md) for detailed documentation.

### ✅ Step 2: Chat Agent (Complete)
Conversational AI agent with tool calling capabilities.

**Implementation:**
- `agent/agent.py`: RestaurantAgent class with Lisette Chat integration
- `agent/system_prompt.txt`: Spanish language instructions with examples
- **Tool 1**: `search_restaurants()` - Search restaurants by cuisine, price, zone, dietary options (13 filters)
- **Tool 2**: `search_dishes()` - Search for specific dishes across all restaurants (10 filters)
- **Tool 3**: `get_walking_time()` - Calculate walking distance between restaurants
- Welcome message in chat history for immediate engagement
- Streaming support for real-time responses

**Key Capabilities:**
- Natural language restaurant recommendations
- Dish-specific queries ("Where can I find tiramisu?")
- Dietary requirement handling at dish level
- Location-based suggestions with walking times

**See:** [`agent/README.md`](agent/README.md) for detailed documentation.

### ✅ Step 3: Web UI (Complete)
Real-time streaming web interface with FastHTML and DaisyUI.

**Implementation:**
- `main.py`: FastHTML app with SSE (Server-Sent Events) streaming
- DaisyUI v5 theme with custom oklch colors (styles.css)
- Real-time word-by-word response streaming
- Markdown rendering for formatted agent responses
- Auto-scroll chat messages
- Responsive centered layout (80vh height, max-width 4xl)
- HTMX for dynamic form submission without page reload

**Features:**
- 🎨 Modern UI with dark grey secondary color theme
- ⚡ Instant input reset after message send
- 📱 Responsive design for mobile and desktop
- 💬 Message type filtering (shows user messages and assistant responses, hides tool calls)
- 🔄 New chat button to reset conversation
- 📄 Custom page title for browser tabs

### 🚧 Step 4: Monitoring (TODO)
Analytics and monitoring functionality.

**Planned Features:**
- Usage tracking and session analytics
- Search query patterns
- Performance metrics (response times, token usage)
- User interaction logs

## Installation

### Prerequisites
- Python 3.12+
- uv package manager (https://docs.astral.sh/uv/)
- Anthropic API key

### Setup

1. Clone the repository
```bash
git clone https://github.com/fbereilh/agent.git
cd agent
```

2. Install dependencies
```bash
uv sync
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

4. Run the web application
```bash
uv run python main.py
```

The app will be available at `http://localhost:5001`

### Docker Setup

Run with Docker Compose:

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your-api-key-here"

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Or build and run manually:

```bash
# Build image
docker build -t restaurant-agent .

# Run container
docker run -p 5001:5001 \
  -e ANTHROPIC_API_KEY="your-api-key-here" \
  -v $(pwd)/chromadb:/app/chromadb \
  restaurant-agent
```

## Quick Start

### Using the Web Interface

1. Start the server: `uv run python main.py` (or `docker-compose up`)
2. Open your browser to `http://localhost:5001`
3. Ask for restaurant recommendations in Spanish (e.g., "Busco comida italiana")
4. Watch the AI response stream in real-time!

### Using the Search Module Programmatically

```python
from search import RestaurantSearch

# Initialize search (uses singleton pattern)
search = RestaurantSearch(db_path="chromadb")
search.load_and_index()

# Search for restaurants
results = search.search(
    query="Italian food with vegan options",
    n_results=3,
    has_vegan=True,
    zone="north"
)

for result in results:
    print(f"{result['metadata']['name']} - {result['metadata']['zone']}")

# Search for specific dishes
dish_results = search.search_dishes(
    query="tiramisu",
    n_results=5,
    has_vegetarian=False
)

for result in dish_results:
    print(f"{result['document']} at {result['metadata']['restaurant_name']}")
```

### Using the Chat Agent Programmatically

```python
from agent import RestaurantAgent

# Initialize agent
agent = RestaurantAgent(db_path="chromadb")

# Chat with the agent
response = agent("Busco un restaurante italiano para cenar")
print(response.content)

# Access chat history
print(len(agent.history))  # All messages including tool calls
```


### Running Tests

```bash
# Run all search tests (4 tests including dish search)
uv run pytest tests/search.py -v

# Run specific test
uv run pytest tests/search.py::test_dish_vector_store_indexing -v

# Run agent tests 
uv run pytest tests/agent.py -v

# Quick validation of dish search
uv run python test_dishes.py
```

**Test Coverage:**
- ✅ Data loading from Google Sheets
- ✅ Restaurant vector store indexing (16 restaurants)
- ✅ Dish vector store indexing (697 dishes)
- ✅ Document builder functions
- ✅ Search functionality with filters
- ✅ Agent initialization and tool calling

### Adding Dependencies

```bash
uv add package-name
```



## Key Features

### 🔍 Dual Semantic Search
- **Restaurant Search**: Natural language queries across 16 restaurants with descriptions
  - 13 filter parameters (price, zone, dietary options, services, time)
  - Top-N results with relevance scoring
  - Restaurant-level recommendations
- **Dish Search**: Find specific dishes across all 697 menu items
  - 10 filter parameters including dietary tags and categories
  - Search for "pasta", "tiramisu", "vegan burger" and find where available
  - Results grouped by restaurant with location context

