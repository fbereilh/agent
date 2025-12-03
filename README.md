# Restaurant Recommendation Agent

An intelligent conversational agent for a shopping mall that helps visitors find the perfect restaurant using semantic search, AI-powered chat, and real-time streaming responses.

## Project Overview

This project implements a complete restaurant recommendation system for La Roca Village mall with:
- **Semantic Search**: Vector-based search across 16 restaurants with natural language queries
- **AI Chat Agent**: Conversational interface with tool calling for dynamic recommendations
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
- **Vector Store**: ChromaDB for semantic search over restaurant data
- **LLM Integration**: Lisette + LiteLLM with Anthropic Claude (Haiku 4.5)
- **Streaming**: Server-Sent Events (SSE) for real-time response rendering
- **Data Source**: Google Sheets (16 restaurants with dishes and metadata)
- **Package Management**: uv for fast, reliable Python dependency management

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
Semantic search system for restaurant discovery.

**Implementation:**
- `search/data_loader.py`: Load from Google Sheets, build searchable documents with top dishes
- `search/search.py`: ChromaDB vector store with 13 metadata filters
- Singleton pattern for efficient search instance reuse
- Persistent vector store

**See:** [`search/README.md`](search/README.md) for detailed documentation.

### ✅ Step 2: Chat Agent (Complete)
Conversational AI agent with tool calling capabilities.

**Implementation:**
- `agent/agent.py`: RestaurantAgent class with Lisette Chat integration
- `agent/system_prompt.txt`: Spanish language instructions with examples
- Tool 1: `search_restaurants()` - 13 filter parameters, returns formatted results in `<valid>` tags
- Tool 2: `get_walking_time()` - Calculate walking distance between restaurants
- Welcome message in chat history for immediate engagement
- Streaming support for real-time responses

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

## Development

### Working with the Notebook

The project's original development was done in `00_develop.ipynb`. This notebook contains:
- Data exploration and analysis
- Search implementation experiments
- Agent tool development and testing
- UI component prototyping

To explore the development process:
```bash
uv run jupyter lab 00_develop.ipynb
```

### Running Tests

```bash
# Run search tests
uv run python -m pytest tests/search.py -v

# Run agent tests 
uv run python -m pytest tests/agent.py -v
```

### Adding Dependencies

```bash
uv add package-name
```

## Data Source

Restaurant and dish data is loaded from a Google Sheets document containing 16 restaurants from La Roca Village. The data includes:
- **Restaurant information**: Name, description, location zone (north/center/south), coordinates, hours
- **Menu items**: Top dishes with keywords and dietary tags
- **Dietary options**: Vegetarian, vegan, gluten-free tags
- **Pricing**: Low/medium/high categorization
- **Services**: Takeaway, bar service, reservations, menu availability
- **Contact**: Phone numbers and website URLs

The data is indexed into ChromaDB with 17 metadata fields for precise filtering and semantic search.

## Key Features

### 🔍 Semantic Search
- Natural language queries across restaurant descriptions and dishes
- 13 filter parameters (price, zone, dietary options, services, time)
- Top-N results with relevance scoring

### 🤖 AI Chat Agent
- Spanish language conversational interface
- Tool calling: `search_restaurants()` and `get_walking_time()`
- Context-aware recommendations based on time of day
- Streaming responses for better UX

### 🎨 Modern Web UI
- Real-time SSE streaming (watch responses appear word-by-word)
- DaisyUI v5 + Tailwind styling with custom color theme
- Responsive centered layout
- Markdown rendering for formatted responses
- Auto-scroll chat messages

## Architecture Highlights

- **Notebook-First Development**: All logic prototyped in `00_develop.ipynb` before modularization
- **Singleton Pattern**: Efficient vector store reuse across agent calls
- **Tool Format Consistency**: Inline parameter comments matching notebook format for LLM clarity
- **Streaming Architecture**: SSE with background threads for non-blocking response generation
- **Clean Separation**: Search logic, agent logic, and UI completely decoupled

## Contributing

This is a demonstration project showcasing:
- Notebook-to-production workflow
- AI-assisted development (GitHub Copilot)
- Modern Python tooling (uv, FastHTML, ChromaDB, Lisette)
- Streaming web interfaces with SSE

Feel free to explore, learn from, and adapt the code!

## License

[To be determined]

## Next Steps

1. ✅ Implement search functionality
2. 🚧 Develop chat agent module
3. 🚧 Build web UI
4. 🚧 Add monitoring capabilities

---

**Current Status:** Step 1 (Search Feature) completed. Ready for Step 2 (Chat Agent).
